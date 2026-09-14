# AI-103 — Day 0: Chuẩn bị Azure và an toàn chi phí

## Mục tiêu của Day 0

Bạn đã có Azure account. Hôm nay **không cần triển khai Azure AI, không cần gọi model, và không cần tạo máy ảo**. Kết quả mong muốn là một môi trường học sạch, dễ xóa, và có cảnh báo chi phí trước khi sang Day 1–2.

Kết thúc Day 0, bạn phải có:

- Biết chính xác subscription nào sẽ dùng để học và trạng thái của nó.
- Một resource group dành riêng cho lab: `rg-ai103-lab`.
- Một budget theo subscription và một budget theo resource group, nếu portal/loại subscription cho phép.
- Biết mở Cost Analysis, đổi đúng scope, lọc đúng resource group và kiểm tra chi phí sau mỗi lab.
- Một nguyên tắc vận hành: tạo ít, thử nhỏ, kiểm tra, xóa ngay thứ không còn dùng.

> **Giới hạn chi tiêu cá nhân đề xuất:** đặt mục tiêu USD 10 cho tháng hiện tại. Đây là *cảnh báo*, không phải cơ chế chặn tiền tự động. Budget của Azure không tự dừng hay xóa resource khi vượt ngưỡng.[^1]

---

## 1. Bức tranh tổng thể: bốn khái niệm cần hiểu trước

| Khái niệm | Hiểu đơn giản | Vai trò trong lúc học AI-103 |
|---|---|---|
| **Tenant / Microsoft Entra ID** | "Tổ chức danh tính" chứa user của bạn | Xác thực đăng nhập; về sau dùng cho RBAC và Managed Identity. |
| **Subscription** | "Tài khoản thanh toán + ranh giới quản trị" | Resource tạo trong subscription mới có thể phát sinh phí. Subscription tự nó không mất phí; các resource bên trong mới có thể mất phí.[^2] |
| **Resource group (RG)** | "Thư mục dự án có vòng đời chung" | Gom toàn bộ lab AI-103 để có thể xem chi phí hoặc xóa một lần. Khi xóa RG, các resource trong nó cũng bị xóa.[^3] |
| **Region** | Khu vực Azure đặt resource | Ảnh hưởng feature/model có sẵn, quota, độ trễ và đơn giá. |

Mô hình bạn sẽ dùng:

```text
Microsoft Entra tenant
        └── Subscription dùng để học
                └── rg-ai103-lab
                        ├── Day 2: Foundry / model deployment
                        ├── Day 5: Azure AI Search
                        ├── Day 7: Document Intelligence
                        └── ... các lab nhỏ, tạm thời
```

Không đưa tài nguyên cá nhân/production vào `rg-ai103-lab`. Mọi resource trong group này phải có thể xóa được khi bạn kết thúc lộ trình.

---

## 2. Nguyên tắc an toàn chi phí (đọc trước khi bấm Create)

1. **Budget ≠ spending cap.** Khi vượt ngưỡng, Azure gửi email/cost alert; resource đang chạy vẫn có thể tiếp tục tính phí.[^1]
2. **Chi phí không hiện tức thì.** Với PAYG, usage/cost có thể mất đến 72 giờ mới xuất hiện trong Cost Management; dữ liệu trong kỳ hiện tại chỉ là ước tính.[^4] Vì thế, không được suy luận "chưa thấy phí = chắc chắn miễn phí".
3. **Budget không thay thế thao tác xóa.** Kết thúc lab phải kiểm tra resource rồi xóa deployment/resource không dùng.
4. **Không mua cam kết dài hạn.** Không dùng Reserved Instances, Savings Plan, Provisioned Throughput hay GPU/VM để ôn thi.
5. **Chỉ tạo theo một lab đã định.** Không mở portal và thử tùy hứng các SKU/feature trả phí.
6. **Dữ liệu test phải nhỏ.** 5–20 tài liệu, vài ảnh/PDF, một đoạn audio/video rất ngắn là đủ cho mục tiêu học.

---

## 3. Bước 1 — Đăng nhập và chọn đúng directory

1. Mở [Azure portal](https://portal.azure.com) và đăng nhập bằng account Azure của bạn.
2. Ở góc trên bên phải, bấm avatar/account. Nếu có nhiều directory, chọn directory chứa subscription bạn định dùng.
3. Trên thanh tìm kiếm của portal, nhập **Subscriptions** và mở kết quả đó.
4. Nếu không thấy subscription, bấm bộ lọc phía trên danh sách, chọn **All**, bỏ tùy chọn chỉ hiển thị subscription đã được chọn trong portal, rồi bấm **Apply**.[^5]

### Cần ghi lại gì?

Trong danh sách Subscriptions, mở subscription bạn sẽ dùng và ghi vào bảng dưới đây. Không chia sẻ Subscription ID ra nơi công khai; nó không phải password nhưng vẫn là định danh môi trường cloud của bạn.

| Trường | Giá trị của bạn | Ý nghĩa / tiêu chí đúng |
|---|---|---|
| Subscription name | `...` | Dễ nhận ra là subscription học/lab. |
| Subscription ID | `...` | Cần khi dùng Azure CLI hoặc support, không cần học thuộc. |
| Status | `Enabled` / `Active` | Phải là trạng thái hoạt động trước khi tạo resource. `Disabled` không thể tạo hay quản lý resource.[^6] |
| Directory (tenant) | `...` | Đúng tenant bạn vừa chọn. |
| Offer / plan | `...` | Biết đây là PAYG, free trial, student, doanh nghiệp… để hiểu quyền và billing. |
| Vai trò của bạn | `Owner` / `Contributor` / khác | Tối thiểu cần quyền tạo resource. Để tạo/quản lý budget ở scope subscription, Owner có đầy đủ quyền; Contributor hoặc Cost Management Contributor có giới hạn nhất định.[^7] |

### Nếu có nhiều subscription, chọn cái nào?

Ưu tiên subscription thỏa cả bốn điều kiện:

- Bạn là **Owner** (hoặc ít nhất Contributor) và có quyền truy cập Cost Management.
- Không chứa workload công việc/production của người khác.
- Có phương thức thanh toán/credit hợp lệ hoặc offer cho phép tạo resource.
- Bạn có thể xóa toàn bộ resource lab trong đó mà không ảnh hưởng ai.

Nếu subscription là của công ty/trường, hãy kiểm tra policy và xác nhận bạn được phép tạo Azure AI resources. Không tự chuyển offer, đổi billing tenant, hoặc thêm phương thức thanh toán chỉ để làm bài lab.

---

## 4. Bước 2 — Xem loại billing và chi phí hiện tại

Mục tiêu: biết **hiện đã có khoản nào không**, và tránh nhìn nhầm scope.

1. Trong portal, tìm **Cost Management + Billing**.
2. Nếu màn hình có nút/chip **Scope**, chọn đúng **subscription học**. Nếu chỉ có một scope, mở **Properties** để xem loại billing account.[^5]
3. Chọn **Cost Management** → **Cost analysis**.
4. Chọn khoảng thời gian **This month**.
5. Lần lượt dùng **Group by**:
   - `Service name`: phát hiện dịch vụ nào tạo phí.
   - `Resource group`: sau này dùng để xác nhận phí của `rg-ai103-lab`.
   - `Resource`: khi cần truy ra resource cụ thể.
6. Ghi lại tổng chi phí hiện tại. Nếu đã có chi phí lạ, đừng xóa bừa: xem `Service name`, `Resource group`, `Resource`, rồi xác định owner trước.

Cost Analysis có thể group theo service, tag, subscription và resource group; nó cũng lọc được theo resource type, tag và thời gian.[^8] Sau khi tạo resource mới, hãy cho dữ liệu thời gian để xuất hiện—Microsoft khuyến nghị chờ khoảng 24 giờ để thấy chi phí trong view, còn PAYG có thể trễ hơn.[^4][^8]

### Thiết lập anomaly alert (khuyến nghị, không bắt buộc)

Anomaly alert tìm biến động chi phí bất thường dựa trên lịch sử. Nó bổ sung cho budget, không thay thế budget.

1. Vẫn ở **Cost Management**, đảm bảo scope là subscription học.
2. Chọn **Cost alerts** → **+ Add**.
3. Ở **Alert type**, chọn **Anomaly**.
4. Điền thông tin bắt buộc, dùng email bạn thường kiểm tra, rồi chọn **Create**.

Tính năng này cần `Cost Management Contributor` hoặc quyền cao hơn; nếu không thấy nút tạo, đó thường là vấn đề permission.[^9] Vì account mới chưa có lịch sử chi phí, alert này có thể chưa hữu ích ngay; vẫn nên ưu tiên budget.

---

## 5. Bước 3 — Tạo resource group học tập

### Tại sao tạo RG trước?

Resource group là container cho resource có chung vòng đời: triển khai cùng, cập nhật cùng, và xóa cùng.[^3] Đây là cách an toàn nhất để giữ lab AI-103 tách biệt. Mặc dù có thể đặt resource ở các vùng khác resource group, Microsoft khuyến nghị cùng location khi có thể.[^10]

### Chọn region: dùng quy tắc này

Không chọn region chỉ vì gần Việt Nam. Với AI-103, feature/model availability quan trọng hơn độ trễ vài chục mili-giây.

1. Mở trang [Foundry region support](https://learn.microsoft.com/azure/foundry/reference/region-support) trước mỗi lab cần Foundry.
2. Chọn một region mà subscription của bạn cho phép và có các dịch vụ cần học.
3. Với lộ trình này, **Southeast Asia** thường là điểm khởi đầu hợp lý về địa lý; tuy nhiên không cam kết dịch vụ/model/SKU nào cũng có tại đó. Danh sách Foundry hiện có Southeast Asia, nhưng Microsoft nói rõ feature availability thay đổi theo vùng và phải kiểm tra từng feature trước khi deploy.[^11]
4. Nếu một model hoặc Azure AI Search không có ở region đó, dùng region hỗ trợ service đó cho **resource của lab**. Ghi region vào tên ghi chú/lab log.

Lưu ý quan trọng: location của **resource group** chủ yếu là nơi Azure Resource Manager lưu metadata và điều phối thao tác quản trị; nó không quyết định endpoint/data-plane của resource.[^10] Vì vậy hãy chọn một region ổn định, thuận tiện để quản lý, rồi xác nhận region cho từng service ở các ngày sau.

### Thao tác trên portal

1. Tìm **Resource groups** trong thanh tìm kiếm portal.
2. Chọn **Create**.
3. Điền:

| Ô trên portal | Giá trị đề xuất | Vì sao |
|---|---|---|
| Subscription | Subscription học đã kiểm tra | Tách chi phí và quyền đúng phạm vi. |
| Resource group | `rg-ai103-lab` | Ngắn, nhất quán, dễ lọc. |
| Region | `Southeast Asia` *hoặc region bạn chọn ở phần trên* | Nơi lưu metadata của RG. |

4. Chọn **Review + create**. Xác nhận validation pass rồi chọn **Create**.
5. Mở RG vừa tạo. Vào **Tags** và thêm các tag sau (tag giúp lọc/đọc chi phí, nhưng tag gắn ở RG không tự truyền sang resource).[^12]

| Name | Value |
|---|---|
| `purpose` | `ai103-learning` |
| `environment` | `lab` |
| `owner` | `your-name-or-alias` |
| `delete-after` | `YYYY-MM-DD` |

6. Bấm **Apply** / **Save** nếu portal yêu cầu.

> Chưa tạo Foundry, AI Search, Storage Account hay bất kỳ Azure AI service nào ở bước này. Việc tạo resource group không phải lab AI trả phí.

### Kiểm tra kết quả

Trong Overview của `rg-ai103-lab`, bạn phải thấy đúng Subscription và Region. Mục **Resources** hiện 0 resource là kết quả đúng cho Day 0.

---

## 6. Bước 4 — Tạo budget cảnh báo

### Thiết kế hai lớp khuyến nghị

| Lớp | Scope | Budget đề xuất | Mục đích |
|---|---|---:|---|
| 1. Bao phủ | Subscription học | USD 10 / tháng | Phát hiện cả chi phí vô tình tạo ngoài RG lab. |
| 2. Lab | `rg-ai103-lab` | USD 8 / tháng | Quy trách nhiệm rõ cho hành trình AI-103. |

Nếu toàn bộ subscription chỉ dành cho AI-103, bạn có thể chỉ dùng budget subscription USD 10 để đơn giản. Nếu subscription chứa việc khác, **bắt buộc** dùng budget theo resource group; budget subscription thấp có thể gây cảnh báo vì chi phí không liên quan.

### Tạo budget cho subscription

1. Từ Azure portal, tìm **Subscriptions** → chọn subscription học.
2. Trong menu bên trái, chọn **Budgets**. Nếu portal hiện chip **Scope**, kiểm tra lần nữa scope đúng là subscription học.
3. Chọn **+ Add**.
4. Điền theo mẫu:

| Trường | Giá trị đề xuất |
|---|---|
| Name | `budget-ai103-subscription-monthly` |
| Reset period | `Monthly` |
| Creation date | hôm nay hoặc ngày đầu kỳ hiện tại |
| Expiration date | ngày bạn dự kiến thi + 1 tháng, hoặc ít nhất 3 tháng sau hôm nay |
| Amount | `10` USD (đổi theo currency portal nếu cần) |

5. Ở **Alert conditions**, tạo các cảnh báo Actual cost (chi phí đã phát sinh):

| Loại | Ngưỡng | Hành động khi nhận email |
|---|---:|---|
| Actual | 50% | Mở Cost Analysis, xác nhận resource nào đã tạo phí. |
| Actual | 75% | Dừng tạo lab mới, kiểm tra tất cả resource/deployment. |
| Actual | 90% | Xóa mọi resource/deployment không thật sự cần cho lab đang làm. |
| Actual | 100% | Dừng lab trả phí; chỉ học lý thuyết/local cho đến kỳ budget sau hoặc khi đã phân tích nguyên nhân. |
| Forecasted | 80% | Nếu Azure dự báo sẽ vượt, kiểm tra ngay dù actual chưa cao. |

6. Với mỗi alert, nhập email bạn kiểm tra mỗi ngày. Nếu mail vào spam, allow-list `azure-noreply@microsoft.com`.[^1]
7. Chọn **Create**.

Budget cần tối thiểu một cost threshold và một email. Actual và forecast alert gửi thông báo thông thường trong khoảng một giờ sau khi được đánh giá; vì có độ trễ này, không dùng nó làm "công tắc ngắt khẩn cấp".[^1]

### Tạo budget cho `rg-ai103-lab`

1. Mở **Resource groups** → `rg-ai103-lab`.
2. Trong menu của RG, chọn **Budgets** → **+ Add**.
3. Tạo với tên `budget-ai103-lab-monthly`, chu kỳ `Monthly`, amount `8` USD và các ngưỡng/email như trên.

Microsoft hỗ trợ budget ở resource-group scope; thao tác đúng là mở resource group trước rồi chọn Budgets.[^1] Nếu bạn không thấy Budgets hoặc không tạo được, chụp lại lỗi và kiểm tra role ở subscription/RG; đừng giả định budget đã tồn tại.

### Xác minh budget thật sự hoạt động

Sau khi tạo, bạn phải nhìn thấy cả budget trong danh sách **Budgets**, với đúng scope, amount, chu kỳ, ngày hết hạn và email. Vào **Cost alerts** để biết nơi xem alert đang active/dismissed.[^13]

---

## 7. Quy trình 3 phút sau mỗi lab (bắt buộc)

Thực hiện ngay sau mọi lab từ Day 2 trở đi:

1. Trong resource group, vào **Overview → Resources**. Xem từng resource còn tồn tại.
2. Với Foundry/Azure OpenAI, xem riêng **model deployments**: xóa deployment không dùng, không chỉ đóng browser.
3. Với Azure AI Search, xem SKU/tier và xóa service sau khi chụp note/kết quả cần thiết.
4. Mở **Cost Management → Cost Analysis**, scope `rg-ai103-lab`, group by `Resource` hoặc `Service name`; ghi nhận chi phí hiện tại và nhớ rằng nó có độ trễ.
5. Nếu lab đã xong, chọn **Delete resource group**, gõ chính xác `rg-ai103-lab` để xác nhận. Chỉ làm khi bạn đã chắc không cần resource/data bên trong nữa—xóa RG sẽ xóa mọi resource thuộc nó.[^3]

Quy trình ngắn này hiệu quả hơn hẳn việc chỉ đặt một budget lớn.

---

## 8. Lỗi thường gặp và cách xử lý

| Dấu hiệu | Nguyên nhân thường gặp | Cách xử lý an toàn |
|---|---|---|
| Không thấy subscription | Sai directory hoặc đang bị filter | Đổi directory; vào Subscriptions và chọn filter `All`.[^5] |
| Status là Disabled/Expired | Subscription không hoạt động | Không tạo resource; xem trang subscription/billing hoặc liên hệ owner. |
| Không có nút Create/Budgets | Thiếu quyền Azure RBAC hoặc cost-management role | Xem **Access control (IAM)**; nhờ Owner cấp quyền theo scope cần thiết. |
| Budget chưa báo dù đã dùng resource | Chi phí/budget evaluation có độ trễ | Ngừng tạo thêm, kiểm tra resource trực tiếp và chờ Cost Management cập nhật. |
| Đã vượt budget mà resource vẫn chạy | Đây là hành vi mặc định của budget | Xóa/scale down resource thủ công; budget chỉ cảnh báo.[^1] |
| Cost Analysis hiện tổng tiền khác mong đợi | Scope hoặc date range sai; dữ liệu chưa hoàn tất | Kiểm tra scope, `This month`, Group by Resource/Service; xem lại sau 24–72 giờ.[^4] |
| Không deploy được dịch vụ/model ở region đã chọn | Region/feature/quota không hỗ trợ | Kiểm tra region support và trang service/model trước khi đổi region.[^11] |

---

## 9. Checklist Day 0 — chỉ tick khi bạn đã tự kiểm tra

- [ ] Đăng nhập đúng Azure directory/tenant.
- [ ] Chọn đúng subscription học; Status là Enabled/Active.
- [ ] Biết subscription có phải môi trường an toàn để làm lab hay không.
- [ ] Mở Cost Analysis ở scope subscription và ghi tổng chi phí hiện tại.
- [ ] Tạo `rg-ai103-lab` với region đã chủ động chọn.
- [ ] Gắn tags `purpose`, `environment`, `owner`, `delete-after` cho RG.
- [ ] Tạo hoặc xác minh budget subscription USD 10/tháng.
- [ ] Tạo hoặc xác minh budget RG USD 8/tháng.
- [ ] Có actual alerts 50%, 75%, 90%, 100% và forecast alert 80%.
- [ ] Xác nhận email nhận alert đúng; kiểm tra spam/allow-list nếu cần.
- [ ] Hiểu rằng budget không dừng chi phí và Cost Analysis có độ trễ.
- [ ] Không có resource AI/VM/Search nào được tạo chỉ vì Day 0.

---

## 10. Bàn giao sang Day 1

Day 0 hoàn tất khi `rg-ai103-lab` tồn tại, có budget/cảnh báo, và resources trong RG vẫn bằng 0. Sang Day 1, bạn chỉ học khái niệm Microsoft Foundry, architecture, models, agents, tools, evaluation, tracing và governance—vẫn có thể học hoàn toàn miễn phí. Chỉ ở Day 2 mới cân nhắc model deployment nhỏ, sau khi dùng Pricing Calculator để ước tính model/region/SKU.[^14]

---

## 11. Nhật ký thiết lập thực tế — đã hoàn thành ngày 14/09/2026

Phần này ghi lại cấu hình đã thực hiện để bạn có thể đối chiếu trước mỗi lab. Không lưu Subscription ID, email, số thẻ, hay thông tin cá nhân trong tài liệu.

| Hạng mục | Trạng thái đã xác nhận | Ghi chú |
|---|---|---|
| Azure directory | Default Directory | Đây là directory có subscription dùng để học. |
| Subscription | `Azure subscription 1` | Plan: **Azure Plan**; Status: **Active**; vai trò hiện tại: **Owner**. Có thể rename sau nếu muốn, không ảnh hưởng resource. |
| Chi phí ban đầu | 0 | Chưa có resource sử dụng tại thời điểm tạo môi trường. |
| Resource group | `rg-ai103-lab` | Đã tạo thành công, Location: **Southeast Asia**. |
| Resource / deployment trong RG | 0 / 0 | Đây là trạng thái đúng trước khi bắt đầu Day 1. |
| Tags | `purpose=ai103-learning`, `environment=lab`, `owner=lqnhat`, `delete-after=2026-12-31` | Dùng để nhận diện và lọc lab. |
| Budget resource group | `budget-ai103-lab-monthly` | Monthly, amount 10 theo currency của billing account, hết hạn 31/12/2026. |
| Cảnh báo budget RG | Actual 50%, 75%, 90%, 100%; Forecasted 80% | Email nhận cảnh báo đã cấu hình; Action group giữ `None`. |
| Budget subscription | `budget-ai103-subscription-monthly` | Monthly, amount 10; dùng để phát hiện resource vô tình tạo ngoài `rg-ai103-lab`. |
| Cost Analysis baseline | Scope `rg-ai103-lab`, This month, Group by Resource | Mốc ban đầu là 0; nhớ rằng dữ liệu Azure có độ trễ. |

### Cách dùng nhật ký này

Trước một lab trả phí, xác nhận bạn đang làm trong `rg-ai103-lab`. Sau lab, mở Cost Analysis tại scope resource group và kiểm tra resources/deployments còn tồn tại. Nếu không còn cần lab, xóa resource hoặc cả RG theo quy trình ở phần 7.

## Sources

[^1]: Microsoft, [Tutorial: Create and manage budgets](https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets), updated June 26, 2025; Microsoft, [Quickstart: Create a budget with Bicep](https://learn.microsoft.com/azure/cost-management-billing/costs/quick-create-budget-bicep), accessed September 14, 2026.
[^2]: Microsoft, [What is a cloud subscription?](https://learn.microsoft.com/azure/cost-management-billing/manage/cloud-subscription), updated 2026.
[^3]: Microsoft, [Use the Azure portal and Azure Resource Manager to manage resource groups](https://learn.microsoft.com/azure/azure-resource-manager/management/manage-resource-groups-portal), updated February 27, 2026.
[^4]: Microsoft, [Understand Cost Management data](https://learn.microsoft.com/azure/cost-management-billing/costs/understand-cost-mgt-data), accessed September 14, 2026.
[^5]: Microsoft, [View your billing accounts in Azure portal](https://learn.microsoft.com/azure/cost-management-billing/manage/view-all-accounts), updated 2026.
[^6]: Microsoft, [Azure subscription states](https://learn.microsoft.com/azure/cost-management-billing/manage/subscription-states), updated 2026.
[^7]: Microsoft, [Quickstart: Create a budget with Bicep](https://learn.microsoft.com/azure/cost-management-billing/costs/quick-create-budget-bicep), section “Prerequisites”.
[^8]: Microsoft, [Plan to manage Azure costs](https://learn.microsoft.com/azure/cost-management-billing/understand/plan-manage-costs), accessed September 14, 2026.
[^9]: Microsoft, [Identify anomalies and unexpected changes in cost](https://learn.microsoft.com/azure/cost-management-billing/understand/analyze-unexpected-charges), accessed September 14, 2026.
[^10]: Microsoft, [What is Azure Resource Manager?](https://learn.microsoft.com/azure/azure-resource-manager/management/overview), updated 2026.
[^11]: Microsoft, [Feature availability across cloud regions — Microsoft Foundry](https://learn.microsoft.com/azure/foundry/reference/region-support), updated 2026.
[^12]: Microsoft, [Use tags to organize your Azure resources and management hierarchy](https://learn.microsoft.com/azure/azure-resource-manager/management/tag-resources), accessed September 14, 2026.
[^13]: Microsoft, [Use cost alerts to monitor usage and spending](https://learn.microsoft.com/azure/cost-management-billing/costs/cost-mgt-alerts-monitor-usage-spending), accessed September 14, 2026.
[^14]: Microsoft, [Plan and manage costs — Microsoft Foundry](https://learn.microsoft.com/azure/foundry/concepts/manage-costs), updated 2026; Microsoft, [Estimate costs with the Azure pricing calculator](https://learn.microsoft.com/azure/cost-management-billing/costs/pricing-calculator), accessed September 14, 2026.
