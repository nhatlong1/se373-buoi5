# README

This is a mirror of [analysis.md](analysis.md)

# Báo cáo phân tích và kết quả kiểm nghiệm Agent Tools và Skills Lab

## Nhiệm vụ

- Cài đặt tool `list_files`
- Cài đặt skill `refund-policy`
- Kiểm thử công cụ
- Kiểm thử các trường hợp nghiệp vụ và trace.

## 1. Kết quả cài đặt tool list_files

Công cụ `list_files` được cài đặt để liệt một thư mục tương đối với `workspace` của stage, chuẩn hóa đường dẫn, sắp xếp theo tên và chặn các hành vi vượt phạm vi workspace.

Kết quả kiểm thử với bốn trường hợp:

1. **Thư mục hợp lệ (`data/policies`)**:
   - Trạng thái: Thành công (`ok: true`).
   - Kết quả trả về:
     ```json
     {
       "ok": true,
       "path": "data/policies",
       "entries": [
         {
           "name": "policy-before-oct.md",
           "path": "data/policies/policy-before-oct.md",
           "type": "file"
         },
         {
           "name": "policy-from-oct.md",
           "path": "data/policies/policy-from-oct.md",
           "type": "file"
         }
       ]
     }
     ```
   - Nhận xét: Danh sách trả về chính xác các mục trực tiếp, phân loại đúng kiểu file và sắp xếp đúng theo tên.
2. **Đường dẫn trỏ vào một file (`data/policies/policy-before-oct.md`)**:
   - Trạng thái: Báo lỗi có cấu trúc (`ok: false`).
   - Mã lỗi: `NOT_A_DIRECTORY`.
   - Thông báo lỗi: `Đây là file, không phải thư mục: data/policies/policy-before-oct.md`.
   - Nhận xét: Không trả danh sách rỗng, thông báo rõ ràng bản chất đường dẫn là file.
3. **Đường dẫn không tồn tại (`data/khong-ton-tai`)**:
   - Trạng thái: Báo lỗi có cấu trúc (`ok: false`).
   - Mã lỗi: `DIRECTORY_NOT_FOUND`.
   - Thông báo lỗi: `Không tìm thấy thư mục: data/khong-ton-tai`.
   - Nhận xét: Phân biệt chính xác giữa thư mục không tồn tại và thư mục rỗng.
4. **Đường dẫn vượt ngoài workspace (`../secret`)**:
   - Trạng thái: Báo lỗi có cấu trúc (`ok: false`).
   - Mã lỗi: `PATH_OUTSIDE_WORKSPACE`.
   - Thông báo lỗi: `Đường dẫn thoát ra ngoài workspace: ../secret`.
   - Nhận xét: Cơ chế resolve ngăn chặn đường dẫn tương đối vượt cấp (`..`), bảo vệ an toàn cho hệ thống bên ngoài workspace.

Toàn bộ 41 unit test tại Stage 01 và 48 unit test tại Stage 02 đều pass.

## 2. Kết quả các trường hợp kiểm thử nghiệp vụ và bằng chứng trace

Toàn bộ các trường hợp kiểm thử được thực thi với mô hình `qwen3.8-flash` thông qua endpoint OpenAI-compatible `http://ai/v1`, ghi nhận trace theo chuẩn định dạng JSONL trong `stage-02-skills/traces/`.

### Trường hợp A: Mua trước ngày đổi chính sách

- **Câu hỏi đầu vào**: "Tôi mua ngày 28/09/2026, yêu cầu hoàn ngày 06/10/2026, chưa kích hoạt. Tôi có được hoàn không?"
- **Tập tin trace**: `stage-02-skills/traces/20261008-002143_4640741a_turn01_c6655f03.jsonl`
- **Kết quả đạt được**:
  - Chính sách áp dụng: Chính sách hoàn tiền trước tháng 10 (ngày mua 28/09/2026 trước 2026-10-01).
  - Căn cứ tài liệu: `data/policies/policy-before-oct.md`.
  - Số ngày đã qua: 8 ngày.
  - Kết luận: Không đủ điều kiện hoàn tiền (quá hạn 7 ngày theo quy định).
- **Vị trí bằng chứng trong trace**:
  - Dòng 1: Sự kiện `user_submitted` nhận câu hỏi từ người dùng.
  - Dòng 4: Sự kiện `tool_started` gọi `read_file` với tham số `{"path": "skills/refund-policy/SKILL.md"}` để nạp hướng dẫn xử lý hoàn tiền.
  - Dòng 8: Sự kiện `tool_started` gọi `read_file` với `{"path": "skills/refund-policy/references/answer-template.md"}` để lấy mẫu trả lời.
  - Dòng 9: Sự kiện `tool_started` gọi `list_files` với `{"path": "data/policies"}` để khám phá các tài liệu chính sách hiện có.
  - Dòng 14: Sự kiện `tool_started` gọi `read_file` với `{"path": "data/policies/policy-before-oct.md"}` để đọc nội dung chính sách cũ.
  - Dòng 17: Sự kiện `model_response` chứa nội dung kết luận không đủ điều kiện theo đúng mẫu biểu.
  - Dòng 18: Sự kiện `run_completed`.

### Trường hợp B: Mua từ ngày đổi chính sách

- **Câu hỏi đầu vào**: "Tôi mua ngày 02/10/2026, yêu cầu hoàn ngày 12/10/2026, chưa kích hoạt. Tôi có được hoàn không?"
- **Tập tin trace**: `stage-02-skills/traces/20261008-002202_37bb4fdd_turn01_ba6f3bb9.jsonl`
- **Kết quả đạt được**:
  - Chính sách áp dụng: Chính sách hoàn tiền từ tháng 10 (ngày mua từ 2026-10-01 trở đi).
  - Căn cứ tài liệu: `data/policies/policy-from-oct.md`.
  - Số ngày đã qua: 10 ngày.
  - Kết luận: Đủ điều kiện hoàn tiền (trong thời hạn 14 ngày, chưa kích hoạt).
  - Phí hoàn tiền: Không thu phí hoàn tiền (miễn phí).
- **Vị trí bằng chứng trong trace**:
  - Dòng 4: Sự kiện `tool_started` gọi `read_file` nạp `skills/refund-policy/SKILL.md`.
  - Dòng 8: Sự kiện `tool_started` gọi `read_file` nạp `skills/refund-policy/references/answer-template.md`.
  - Dòng 9: Sự kiện `tool_started` gọi `list_files` thư mục `data/policies`.
  - Dòng 14: Sự kiện `tool_started` gọi `read_file` với `{"path": "data/policies/policy-from-oct.md"}`.
  - Dòng 17: Sự kiện `model_response` kết luận đủ điều kiện và không thu phí theo đúng chính sách mới.
  - Dòng 18: Sự kiện `run_completed`.

### Trường hợp thiếu thông tin

- **Câu hỏi đầu vào**: "Tôi mua ngày 02/10/2026, muốn hoàn ngày 12/10/2026."
- **Tập tin trace**: `stage-02-skills/traces/20261008-002217_3b686147_turn01_a3472e31.jsonl`
- **Kết quả đạt được**:
  - Agent tiếp nhận ngày mua và ngày yêu cầu hoàn tiền (10 ngày), nhưng phát hiện thiếu trạng thái kích hoạt sản phẩm.
  - Agent chủ động dừng lại, không kết luận vội vã và đặt câu hỏi làm rõ: "Sản phẩm của bạn đã được kích hoạt chưa?".
  - Agent nêu rõ hai khả năng dựa trên câu trả lời sắp tới của khách hàng và tuyệt đối không tự giả định trạng thái "chưa kích hoạt".
- **Vị trí bằng chứng trong trace**:
  - Dòng 4: Nạp `skills/refund-policy/SKILL.md`.
  - Dòng 8 và 9: Nạp template và quét danh sách file trong `data/policies`.
  - Dòng 14: Đọc `data/policies/policy-from-oct.md`.
  - Dòng 17: Phản hồi của mô hình yêu cầu người dùng xác nhận tình trạng kích hoạt, không đưa ra kết luận phê duyệt khi dữ kiện chưa hoàn tất.

### Trường hợp đổi tên file chính sách

Hai tập tin chính sách ban đầu được đổi tên lần lượt thành:
- `policy-before-oct.md` đổi thành `chinh-sach-truoc-thang-10.md`
- `policy-from-oct.md` đổi thành `chinh-sach-tu-thang-10.md`

Hai trường hợp A và B được thực thi lại trong các phiên trò chuyện hoàn toàn mới:

1. **Trường hợp A sau khi đổi tên file**:
   - **Tập tin trace**: `stage-02-skills/traces/20261008-002242_5833e889_turn01_3f51940f.jsonl`
   - **Bằng chứng trong trace**:
     - Dòng 9: Sự kiện gọi `list_files` với `data/policies` trả về danh sách file mới chứa `chinh-sach-truoc-thang-10.md`.
     - Dòng 14: Agent tự động nhận diện và gọi `read_file` với `data/policies/chinh-sach-truoc-thang-10.md`.
     - Dòng 17: Agent kết luận chính xác 8 ngày, quá hạn 7 ngày, không đủ điều kiện hoàn tiền, trích dẫn đúng đường dẫn tài liệu mới `data/policies/chinh-sach-truoc-thang-10.md`.

2. **Trường hợp B sau khi đổi tên file**:
   - **Tập tin trace**: `stage-02-skills/traces/20261008-002258_dcee4c73_turn01_11583221.jsonl`
   - **Bằng chứng trong trace**:
     - Dòng 9: Sự kiện gọi `list_files` với `data/policies`.
     - Dòng 14 và 15: Agent gọi `read_file` đọc nội dung các file đã đổi tên `chinh-sach-truoc-thang-10.md` và `chinh-sach-tu-thang-10.md`.
     - Dòng 19: Agent kết luận đủ điều kiện hoàn tiền, 10 ngày, không thu phí, trích dẫn đúng đường dẫn tài liệu mới `data/policies/chinh-sach-tu-thang-10.md`.

## 3. Trả lời câu hỏi cuối bài

### Câu hỏi: Vì sao cần tool để tìm file và skill để hướng dẫn chọn chính sách?

1. **Vai trò của tool tìm file (`list_files`)**:
   - LLM không có hiểu biết trực tiếp về hệ thống tệp cục bộ của máy. Nếu không có công cụ như `list_files` và framework hỗ trợ gọi tool, mô hình hoàn toàn mù về cấu trúc thư mục thực tế tại thời điểm chạy.
   - Nhờ có `list_files`, mô hình có khả năng tương tác với môi trường, ví dụ như tự động khám phá danh mục tài liệu, thích ứng khi tài liệu được cập nhật, nhờ đó lập trình viên có thể bổ sung nội dung hoặc đổi tên file mà không cần phải sửa đổi mã nguồn/prompt hay can thiệp thủ công.

2. **Vai trò của skill (`refund-policy`)**:
   - Skill là một quy trình vận hành tiêu chuẩn được đóng gói độc lập. Skill cung cấp:
     - Logic nghiệp vụ phức tạp: Hướng dẫn so khớp phạm vi ngày hiệu lực dựa trên ngày mua hàng (thay vì lấy ngày hiện tại của máy).
     - Guardrail: Quy định rõ điều kiện dừng khi thiếu thông tin, giảm thiểu tình trạng mô hình tự suy diễn hoặc giả định trạng thái của khách hàng và đưa ra câu trả lời trái chính sách.
     - Quy chuẩn trình bày: Hướng dẫn chuẩn khuôn mẫu thống nhất cho đầu ra thông qua tài liệu tham chiếu (`references/answer-template.md`), mang lại cảm giác chuyên nghiệp và đồng bộ cho các khách hàng.
   - Việc thiết kế skill theo mô hình progressive disclosure (hiển thị metadata trong prompt gốc, LLM tự nạp toàn văn khi đánh giá yêu cầu khớp mô tả) giúp tiết kiệm dung lượng ngữ cảnh và giảm thiểu tối đa hiện tượng phân tâm.

### Câu hỏi: Nếu agent chưa có tool tìm file, việc sửa prompt có giải quyết được yêu cầu đổi tên file không? Giải thích.

Việc sửa prompt có thể giải quyết yêu cầu đổi tên file, nhưng không giải quyết được một cách bền vững và tổng quát.

1. **Tính chất tĩnh của prompt đối lập với tính chất động của dữ liệu**:
   - Khi không có tool tìm file, agent phụ thuộc hoàn toàn vào việc có đường dẫn tập tin trong prompt (ví dụ ghi rõ `data/policies/policy-before-oct.md`).
   - Nếu tập tin bị đổi tên trong tương lai, được tạo phiên bản mới (ví dụ `policy_v2.md`), hoặc do bên thứ ba thay đổi cấu trúc lưu trữ, prompt sẽ ngay lập tức trở nên lỗi thời. Agent sẽ gặp lỗi `FILE_NOT_FOUND` và quy trình bị sụp đổ. Tệ hơn, agent có thể tùy tiện đoán đường dẫn khi đường dẫn cũ không đọc được, gây lãng phí thời gian, tiền API, và có thể trả lời sai hoặc không liên quan.
   - Việc liên tục sửa prompt mỗi khi có thay đổi trên hệ thống tệp là giải pháp thủ công chắp vá, triệt tiêu tính tự chủ của hệ thống agent.

2. **Gánh nặng dung lượng ngữ cảnh khi nhúng trực tiếp**:
   - Nếu cố gắng giải quyết bằng cách dán toàn bộ nội dung chính sách vào thẳng prompt, chi phí token sẽ gia tăng trên mọi lượt hội thoại (kể cả những câu hỏi không liên quan đến hoàn tiền).
   - Phương pháp này phá vỡ tính phân tách trách nhiệm giữa logic hệ thống và dữ liệu nghiệp vụ, đồng thời làm giảm độ tập trung và suy giảm chất lượng suy luận của mô hình đối với các tác vụ khác.

Vì vậy, chỉ có cơ chế kết hợp giữa công cụ khảo sát động (`list_files`) và kỹ năng định hướng quy trình (`refund-policy`) mới xử lý trọn vẹn bài toán thay đổi tập tin trên môi trường thực tế.