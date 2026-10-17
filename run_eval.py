"""Script chạy các trường hợp kiểm tra cho stage-02-skills để sinh trace thật."""

import shutil
import uuid
from pathlib import Path
from langchain_core.messages import AIMessage, HumanMessage

import paths
from agent import build_agent, build_model, capabilities
from config import PROJECT_NAME, RECURSION_LIMIT, load_settings
from observer import Observer
from trace import TraceWriter


def run_one_turn(prompt: str, conversation_id: str | None = None, history: list | None = None) -> tuple[str, Path, list]:
    settings, missing = load_settings()
    if missing:
        raise RuntimeError(f"Thiếu cấu hình: {missing}")
    
    conv_id = conversation_id or uuid.uuid4().hex
    observer = Observer(conversation_id=conv_id)
    run_id = uuid.uuid4().hex
    observer.start_turn(run_id)
    writer = TraceWriter(paths.TRACES_DIR, PROJECT_NAME, conv_id, run_id, observer.chat_turn)
    
    working = list(history or []) + [HumanMessage(content=prompt)]
    
    def emit(event_type: str, data: dict | None = None):
        event = observer.record(event_type, data)
        writer.write(event)
        
    caps = capabilities()
    emit("user_submitted", {"text": prompt, "tools": caps["tools"], "skills": caps["skills"]})
    observer.sync_messages(working)
    
    agent = build_agent(build_model(settings))
    stream = agent.stream(
        {"messages": working},
        config={"recursion_limit": RECURSION_LIMIT},
        stream_mode=["updates", "custom"],
    )
    
    for mode, chunk in stream:
        if mode == "custom" and isinstance(chunk, dict) and chunk.get("observer"):
            emit(chunk["event"], chunk["data"])
        elif mode == "updates" and isinstance(chunk, dict):
            for update in chunk.values():
                if isinstance(update, dict) and update.get("messages"):
                    working.extend(update["messages"])
                    observer.sync_messages(working)
                    
    ans = ""
    for message in reversed(working):
        if isinstance(message, AIMessage) and not message.tool_calls:
            ans = str(message.content)
            break
            
    emit("run_completed", {"answer_chars": len(ans)})
    print(f"\n--- [Conv: {conv_id[:8]}] ---")
    print(f"User: {prompt}")
    print(f"Assistant: {ans}")
    print(f"Trace saved to: {writer.path}")
    return ans, writer.path, working


def main():
    print("=== Chạy kiểm tra các trường hợp ===")
    
    # Trường hợp A: Mua trước ngày đổi chính sách
    prompt_a = "Tôi mua ngày 28/09/2026, yêu cầu hoàn ngày 06/10/2026, chưa kích hoạt. Tôi có được hoàn không?"
    print("\n>>> 1. Trường hợp A:")
    ans_a, trace_a, _ = run_one_turn(prompt_a)
    
    # Trường hợp B: Mua từ ngày đổi chính sách
    prompt_b = "Tôi mua ngày 02/10/2026, yêu cầu hoàn ngày 12/10/2026, chưa kích hoạt. Tôi có được hoàn không?"
    print("\n>>> 2. Trường hợp B:")
    ans_b, trace_b, _ = run_one_turn(prompt_b)
    
    # Trường hợp Thiếu thông tin
    prompt_missing = "Tôi mua ngày 02/10/2026, muốn hoàn ngày 12/10/2026."
    print("\n>>> 3. Trường hợp Thiếu thông tin:")
    ans_missing, trace_missing, _ = run_one_turn(prompt_missing)
    
    # Đổi tên file trong workspace/data/policies
    print("\n>>> 4. Đổi tên file...")
    policies_dir = paths.WORKSPACE_DIR / "data" / "policies"
    old_file = policies_dir / "policy-before-oct.md"
    new_file = policies_dir / "policy-from-oct.md"
    renamed_old = policies_dir / "chinh-sach-truoc-thang-10.md"
    renamed_new = policies_dir / "chinh-sach-tu-thang-10.md"
    
    shutil.move(old_file, renamed_old)
    shutil.move(new_file, renamed_new)
    
    try:
        # Trường hợp A sau đổi tên
        print("\n>>> 5. Trường hợp A sau khi đổi tên file:")
        ans_a_renamed, trace_a_renamed, _ = run_one_turn(prompt_a)
        
        # Trường hợp B sau đổi tên
        print("\n>>> 6. Trường hợp B sau khi đổi tên file:")
        ans_b_renamed, trace_b_renamed, _ = run_one_turn(prompt_b)
    finally:
        # Khôi phục file hoặc giữ cả hai tên để chắc chắn
        shutil.copy(renamed_old, old_file)
        shutil.copy(renamed_new, new_file)
        print("\n>>> Đã giữ cả file gốc và file đổi tên.")

    print("\n=== Hoàn tất chạy tất cả các trường hợp ===")


if __name__ == "__main__":
    main()
