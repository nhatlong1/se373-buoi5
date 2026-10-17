---
name: refund-policy
description: Hướng dẫn kiểm tra điều kiện hoàn tiền và tính phí hoàn tiền theo chính sách. Dùng khi người dùng hỏi về hoàn tiền, trả hàng, chính sách hoàn tiền, hoặc kiểm tra xem một đơn hàng có được hoàn tiền hay không.
---

# Refund policy

Hướng dẫn xử lý yêu cầu hoàn tiền và kiểm tra điều kiện hoàn tiền của khách hàng.

## Quy trình thực hiện

1. **Kiểm tra thông tin đầu vào từ câu hỏi của người dùng**:
   Cần đủ 3 thông tin bắt buộc:
   - **Ngày mua hàng** (purchase date).
   - **Ngày yêu cầu hoàn tiền** (refund request date).
   - **Trạng thái kích hoạt sản phẩm** (đã kích hoạt hay chưa kích hoạt).

   *LƯU Ý QUAN TRỌNG VỀ THIẾU THÔNG TIN*: Nếu thiếu bất kỳ thông tin nào trong 3 thông tin trên (đặc biệt là trạng thái kích hoạt sản phẩm), **dừng lại ngay và hỏi người dùng** để bổ sung thông tin còn thiếu trước khi đưa ra kết luận. Tuyệt đối **không tự giả định** (ví dụ: không được tự giả định sản phẩm "chưa kích hoạt").

2. **Đọc template câu trả lời**:
   - Sử dụng tool `read_file` để đọc file template tại `skills/refund-policy/references/answer-template.md`.

3. **Tìm và đọc tài liệu chính sách**:
   - Sử dụng tool `list_files` với đường dẫn `data/policies` để liệt kê các tài liệu chính sách hiện có trong thư mục (không cố định tên file vì file có thể bị đổi tên).
   - Sử dụng tool `read_file` để đọc nội dung các file chính sách tìm được trong `data/policies/`.

4. **Xác định chính sách áp dụng và điều kiện**:
   - Căn cứ vào **ngày mua hàng** để chọn chính sách phù hợp theo phạm vi hiệu lực ghi trong tài liệu:
     - Ngày mua trước `2026-10-01`: Áp dụng chính sách hoàn tiền trước tháng 10.
     - Ngày mua từ `2026-10-01` trở đi (bao gồm ngày này): Áp dụng chính sách hoàn tiền từ tháng 10.
   - **Tính số ngày đã qua**: Số ngày là chênh lệch ngày lịch giữa ngày yêu cầu hoàn tiền và ngày mua hàng. Sử dụng ngày yêu cầu trong câu hỏi, không dùng ngày hiện tại của máy. Bằng đúng giới hạn quy định vẫn đủ điều kiện về thời gian.
   - **Kiểm tra điều kiện hoàn tiền**:
     - Nếu sản phẩm **đã kích hoạt**: Không hoàn tiền trong mọi trường hợp.
     - Nếu sản phẩm **chưa kích hoạt**:
       - Với chính sách trước tháng 10: Thời hạn yêu cầu hoàn tiền trong vòng 7 ngày kể từ ngày mua. Nếu số ngày <= 7: Đủ điều kiện, phí hoàn tiền là 10% giá trị đơn hàng. Nếu số ngày > 7: Không đủ điều kiện (quá thời hạn 7 ngày).
       - Với chính sách từ tháng 10: Thời hạn yêu cầu hoàn tiền trong vòng 14 ngày kể từ ngày mua. Nếu số ngày <= 14: Đủ điều kiện, không thu phí hoàn tiền (miễn phí). Nếu số ngày > 14: Không đủ điều kiện (quá thời hạn 14 ngày).

5. **Trả lời người dùng**:
   - Trình bày câu trả lời theo đúng định dạng trong `references/answer-template.md`, bao gồm đầy đủ các mục:
     - Chính sách áp dụng
     - Căn cứ tài liệu (đường dẫn file tương đối trong workspace, ví dụ `data/policies/...`)
     - Số ngày đã qua (tính từ ngày mua đến ngày yêu cầu hoàn)
     - Kết luận (đủ điều kiện hoặc không đủ điều kiện)
     - Phí hoàn tiền (nếu đủ điều kiện) hoặc lý do từ chối (nếu không đủ điều kiện).
