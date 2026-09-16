# AI-103 — Nguồn học và practice đã sàng lọc

> Microsoft Learn/study guide là **nguồn đúng-sai cuối cùng**. Nguồn community hữu ích để có thêm scenario, lab hoặc cách ôn, nhưng phải kiểm chứng vì AI-103/Foundry đổi terminology, role và API nhanh.

## Dùng làm trục chính (official)

| Nguồn | Dùng khi nào | Cách dùng |
|---|---|---|
| [AI-103 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103) | Trước khi học một domain, khi hai nguồn mâu thuẫn | Map topic vào skills measured; đây là blueprint hiện hành (16/04/2026). |
| [AI-103T00-A course](https://learn.microsoft.com/en-us/training/courses/ai-103t00) | Muốn một curriculum chính thức hoàn chỉnh | Dùng module phù hợp sau lab, không cần làm tuần tự toàn bộ trước khi practice. |
| [Develop AI agents on Azure](https://learn.microsoft.com/en-us/training/paths/develop-ai-agents-azure/) | Days 3–4 | Làm module prompt agent trước; tools/MCP/workflow/multi-agent theo đúng ngày kế tiếp. |
| [Practice Assessment + Exam Sandbox](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-apps-and-agents-developer-associate/) | Từ Day 7 và Day 14 | Là baseline/thi thử chính thức; dùng để đo gap, không học thuộc đáp án. |

## Community sources đáng dùng, có điều kiện

| Nguồn | Giá trị | Cách dùng an toàn |
|---|---|---|
| [kkaminsk/AI-103-Study-Guide](https://github.com/kkaminsk/AI-103-Study-Guide) | Guide theo 5 exam domains, có cập nhật theo blueprint 2026 và link Microsoft Learn. | Đọc Guide 1 song song Days 2–6; bấm link Microsoft Learn để xác thực facts drift-prone. |
| [sefstratiou-ai/ai-103-practice-exam](https://github.com/sefstratiou-ai/ai-103-practice-exam) | Practice simulator local: 226 câu original, chế độ study/timed, explanation và link docs từng câu. | Từ Day 5: 10–15 câu/domain ở study mode. Day 10/14: một lượt timed; ghi error log theo domain. |
| [ntufar/AI-103](https://github.com/ntufar/AI-103) | Workspace có guide, quick reference, lab, mock runner và rubric. | Mượn structure/lab rubric; kiểm tra mọi Azure/Foundry API, role và SKU với docs official vì repo không phải nguồn Microsoft. |
| [tpriyadata/microsoft-ai-103-study-guide](https://github.com/tpriyadata/microsoft-ai-103-study-guide) | Nhiều scenario/practice và code patterns. | Dùng như question bank phụ khi đã làm official + simulator; chỉ giữ đáp án được Microsoft Learn xác nhận. |

## Không dùng làm nguồn đáp án chính

| Nguồn | Quyết định | Lý do |
|---|---|---|
| [Rahul Mahadik guide](https://rahulmahadik.github.io/ai-103-certification-study-guide/) | Tham khảo nhẹ | Không kiểm tra được nội dung qua lần review này; không dùng cho facts/API hiện hành. |
| [K21 Academy mock tests](https://github.com/k21academyuk/AI-103-Mock-Tests) | Backup practice | Không có bảo chứng official; dùng để phát hiện topic yếu, sau đó kiểm chứng đáp án. |
| [ExamBase / ai-103-exam.com](https://www.ai-103-exam.com/practice-questions/1) | Không đưa vào routine | Third-party question site; độ chính xác/nguồn gốc không bảo đảm. Không dùng để học thuộc hoặc suy đoán đề thật. |

## Routine practice đã cập nhật

1. **Mỗi ngày:** 5 phút ôn flashcards/error log của ngày trước.
2. **Sau lab:** 8–12 câu scenario đúng domain vừa học, làm trước khi xem đáp án.
3. **Mỗi 3 ngày (từ Day 5):** 20–25 câu mixed; phân loại sai theo service selection, security/RBAC, cost/quota, API/SDK, hay architecture.
4. **Day 10 và Day 14:** một full practice assessment/simulator timed; ưu tiên review lỗi hơn làm thêm đề.
5. **Quy tắc kiểm chứng:** câu nào nhắc role, API object, deployment type, quota, SKU hoặc preview feature đều phải có link Microsoft Learn trước khi thành flashcard.

## Lưu ý an toàn

- Không chạy `curl | bash` hoặc script install từ danh sách nguồn khi chưa đọc vendor documentation.
- Không commit `.env`, API keys, subscription IDs hay output chứa token.
- Không dùng exam dumps, leaked/recalled questions hay nội dung vi phạm exam policy.
