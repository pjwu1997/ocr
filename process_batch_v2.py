import os
import sys
import shutil
import tempfile
import signal
import logging
import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import opencc
from paddleocr import PaddleOCRVL

# --- 1. 設定參數 ---
INPUT_ROOT = "/home/asiamath/Documents/題庫網/整理後的數學題庫"
OUTPUT_ROOT = "/home/asiamath/Documents/題庫網/processed_docs_final2"
VLLM_URL = "http://localhost:8000/v1"
MAX_WORKERS = 2
FILE_TIMEOUT = 120

# 定義 Log 檔案路徑
LOG_SUCCESS = os.path.join(OUTPUT_ROOT, "_log_success.txt")
LOG_ERROR = os.path.join(OUTPUT_ROOT, "_log_error.txt")

# --- 2. 靜音與系統設定 ---
os.environ["GLOG_minloglevel"] = "3"
os.environ["PADDLE_INFERENCE_LOG_LEVEL"] = "0"
os.environ["FLAGS_eager_delete_tensor_gb"] = "0.0"

class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._devnull = open(os.devnull, 'w')
        sys.stdout = self._devnull
        sys.stderr = self._devnull

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self._devnull.close()

class TimeoutException(Exception): pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timeout")

# --- 3. Worker 核心邏輯 ---

def process_single_file(args):
    src_path, dest_folder = args
    filename = os.path.basename(src_path)
    base_name = os.path.splitext(filename)[0]
    final_md_name = f"{base_name}.md"
    final_md_path = os.path.join(dest_folder, final_md_name)
    
    # 🔇 關閉 Log
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("paddlex").setLevel(logging.WARNING)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(FILE_TIMEOUT)

    print(f"processing file {filename}...", flush=True)

    try:
        # A. 預測
        with SuppressOutput():
            cc = opencc.OpenCC('s2t')
            pipeline = PaddleOCRVL(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_chart_recognition=False,
                vl_rec_backend="vllm-server",
                vl_rec_server_url=VLLM_URL
            )
            output_gen = pipeline.predict(src_path)
            results = list(output_gen)

        if not results:
            return f"⚠️ Skip (No Result): {filename}"

        # B. 隔離存檔
        with tempfile.TemporaryDirectory() as temp_dir:
            saved_something = False
            for res in results:
                with SuppressOutput():
                    res.save_to_markdown(save_path=temp_dir)
                
                generated_files = [f for f in os.listdir(temp_dir) if f.endswith(".md")]
                if not generated_files: continue

                temp_md_path = os.path.join(temp_dir, generated_files[0])
                
                try:
                    with open(temp_md_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    converted_content = cc.convert(content)
                    
                    mode = 'a' if saved_something else 'w'
                    with open(final_md_path, mode, encoding="utf-8") as f:
                        if saved_something: f.write("\n\n")
                        f.write(converted_content)
                    
                    saved_something = True
                    os.remove(temp_md_path)

                except Exception as e:
                    return f"❌ Write Error ({filename}): {e}"

            if not saved_something:
                 return f"⚠️ Save Failed (Empty): {filename}"
        
        print(f"processing file {filename} success", flush=True)
        return None # 成功回傳 None

    except TimeoutException:
        print(f"⏰ Timeout: {filename}", flush=True) 
        return f"⏰ Timeout ({FILE_TIMEOUT}s): {filename}"
    except Exception as e:
        print(f"❌ Error: {filename}", flush=True)
        return f"❌ System Error ({filename}): {str(e)}"
    finally:
        signal.alarm(0)

# --- 4. 主程式 ---

def main():
    print(f"📂 來源: {INPUT_ROOT}")
    print(f"⚡ Workers: {MAX_WORKERS}")
    
    if not os.path.exists(INPUT_ROOT): return
    if not os.path.exists(OUTPUT_ROOT): os.makedirs(OUTPUT_ROOT)

    # --- 初始化 Log 檔案 (清空舊的) ---
    print("📝 初始化 Log 檔案...")
    with open(LOG_SUCCESS, "w", encoding="utf-8") as f:
        f.write(f"=== 成功清單 (Start: {datetime.datetime.now()}) ===\n")
    with open(LOG_ERROR, "w", encoding="utf-8") as f:
        f.write(f"=== 失敗清單 (Start: {datetime.datetime.now()}) ===\n")

    tasks = []
    print("🔍 掃描檔案中...")
    for root, dirs, files in os.walk(INPUT_ROOT):
        rel_path = os.path.relpath(root, INPUT_ROOT)
        target_dir = os.path.join(OUTPUT_ROOT, rel_path)
        if not os.path.exists(target_dir): os.makedirs(target_dir)
            
        for file in files:
            if file.lower().endswith('.pdf'):
                src_file = os.path.join(root, file)
                tasks.append((src_file, target_dir))

    total_files = len(tasks)
    print(f"📊 總共 {total_files} 個檔案，開始平行處理...")
    print("-" * 40)

    # 使用 'a' (append) 模式開啟 Log 檔，準備持續寫入
    # 我們在 loop 外開啟檔案，避免頻繁開關檔案造成 I/O 負擔
    f_succ = open(LOG_SUCCESS, "a", encoding="utf-8")
    f_err = open(LOG_ERROR, "a", encoding="utf-8")

    try:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_file = {executor.submit(process_single_file, task): task[0] for task in tasks}
            
            pbar = tqdm(as_completed(future_to_file), total=total_files, unit="file", ncols=100, mininterval=1.0)
            
            for future in pbar:
                src_file_path = future_to_file[future]
                filename = os.path.basename(src_file_path)
                current_time = datetime.datetime.now().strftime("%H:%M:%S")

                result = future.result()
                
                # --- 🔥 核心修改：即時寫入 Log ---
                if result is None:
                    # 成功 (Result is None)
                    f_succ.write(f"[{current_time}] {filename}\n")
                    f_succ.flush() # 強制寫入硬碟，讓你立刻看得到
                else:
                    # 失敗 (Result 是錯誤字串)
                    pbar.write(result) # 在終端機顯示紅字
                    f_err.write(f"[{current_time}] {filename} -> {result}\n")
                    f_err.flush()  # 強制寫入硬碟

    finally:
        # 確保程式結束或中斷時關閉檔案
        f_succ.close()
        f_err.close()

    print("-" * 40)
    print(f"✅ 批次處理完成！")
    print(f"🟢 成功列表: {LOG_SUCCESS}")
    print(f"🔴 失敗列表: {LOG_ERROR}")

if __name__ == "__main__":
    main()