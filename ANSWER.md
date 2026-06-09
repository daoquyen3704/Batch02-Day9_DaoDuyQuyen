# BÁO CÁO KẾT QUẢ THỰC HÀNH CODELAB

## HỆ THỐNG MULTI-AGENT VỚI A2A PROTOCOL

### THÔNG TIN CÁ NHÂN

- **Họ và tên:** Đào Duy Quyền
- **Mã học viên:** 2A202600676
- **Lớp:** E403

---

## PHẦN A: TRẢ LỜI CÂU HỎI LÝ THUYẾT & PHÂN TÍCH CODE

### PHẦN 1: Direct LLM Calling

**1. LLM được khởi tạo như thế nào?**

- LLM được tạo trong [common/llm.py](common/llm.py) thông qua hàm `get_llm()`.
- Repo hiện hỗ trợ 2 chế độ:
  - `LLM_PROVIDER=openrouter`: dùng `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`.
  - `LLM_PROVIDER=custom`: dùng `CUSTOM_LLM_API_KEY`, `CUSTOM_LLM_MODEL`, `CUSTOM_LLM_BASE_URL`.
- Với cấu hình hiện tại, `get_llm()` trả về một `ChatOpenAI` trỏ tới OpenAI-compatible endpoint của provider đã chọn. Trong môi trường lab của tôi, cấu hình `custom` dùng DashScope compatible mode với `qwen-max`.

**2. Message được gửi đến LLM có cấu trúc gì?**

- Danh sách message gửi vào model là một mảng gồm:
  - `SystemMessage`: đặt vai trò, quy tắc và định dạng đầu ra.
  - `HumanMessage`: chứa câu hỏi cụ thể của người dùng.

**3. Tại sao cần `SystemMessage` và `HumanMessage`?**

- `SystemMessage` dùng để:
  - định hình vai trò chuyên gia của model,
  - giới hạn phạm vi trả lời,
  - kiểm soát phong cách và độ dài câu trả lời.
- `HumanMessage` dùng để:
  - đưa câu hỏi thực tế vào phiên chat,
  - tách input người dùng khỏi chỉ dẫn hệ thống.
- Việc tách rõ hai loại message giúp model trả lời đúng trọng tâm và giảm nguy cơ prompt injection.

---

### PHẦN 2: LLM + RAG & Tools

**1. `@tool` decorator được dùng ở đâu?**

- Trong [stages/stage_2_rag_tools/main.py](stages/stage_2_rag_tools/main.py), `@tool` được dùng cho:
  - `search_legal_database(query: str) -> str`
  - `calculate_damages(breach_type: str, contract_value: float) -> str`
  - `check_statute_of_limitations(case_type: str) -> str`

**2. `LEGAL_KNOWLEDGE` được cấu trúc như thế nào?**

- `LEGAL_KNOWLEDGE` là một `list` các `dict`, mỗi phần tử có:
  - `id`: định danh ngắn của nguồn luật.
  - `keywords`: danh sách từ khóa để match.
  - `text`: nội dung kiến thức pháp lý trả về cho model.
- Trong phiên bản hiện tại, list này gồm:
  - `ucc_breach`
  - `nda_trade_secret`
  - `dtsa_details`
  - `liquidated_damages`
  - `injunctive_relief`
  - `labor_law`

**3. LLM được bind với tools ra sao?**

- Trong Stage 2, LLM được bind bằng:

```python
llm_with_tools = llm.bind_tools(TOOLS)
```

- `TOOLS` là danh sách các hàm đã gắn `@tool`.
- Cách này chuyển signature của hàm thành tool schema để model có thể tự quyết định gọi tool nào.

---

### PHẦN 3: Single Agent với ReAct

**1. `create_react_agent()` là gì?**

- Đây là helper của LangGraph để dựng agent kiểu ReAct.
- Agent có thể tự:
  - suy luận cần làm gì,
  - gọi tool,
  - đọc kết quả,
  - lặp lại nếu cần.

**2. So sánh với Stage 2**

- Stage 2 phải tự viết vòng lặp manual để kiểm tra `tool_calls`, chạy tool và trả kết quả lại cho model.
- Stage 3 dùng `create_react_agent()` nên LangGraph tự điều phối vòng Think -> Act -> Observe.

**3. Thiết lập trong project của tôi**

- File Stage 3 là [stages/stage_3_single_agent/main.py](stages/stage_3_single_agent/main.py).
- Tôi đã bật `debug=True` thay vì `verbose=True`, vì version LangGraph trong môi trường hiện tại không nhận `verbose`.
- Tools Stage 3 đang dùng:
  - `search_legal_database`
  - `calculate_penalty`
  - `check_compliance_requirements`
  - `search_case_law`

---

### PHẦN 4: Multi-Agent In-Process

**1. `class LegalState(TypedDict)` là gì?**

- Đây là shared state của graph Stage 4 trong [stages/stage_4_milti_agent/main.py](stages/stage_4_milti_agent/main.py).
- State hiện có:
  - `question`
  - `law_analysis`
  - `needs_tax`
  - `needs_compliance`
  - `needs_privacy`
  - `tax_result`
  - `compliance_result`
  - `privacy_result`
  - `final_answer`

**2. Các agent functions là gì?**

- Stage 4 hiện có các node:
  - `analyze_law`
  - `check_routing`
  - `call_privacy_specialist`
  - `call_tax_specialist`
  - `call_compliance_specialist`
  - `aggregate`

**3. `Send()` API dùng để làm gì?**

- `Send()` được dùng để dispatch song song nhiều branch.
- Trong project này, router có thể gửi đồng thời:
  - privacy specialist
  - tax specialist
  - compliance specialist

**4. Graph visualization**

- Tôi đã thêm hàm render graph và lưu file PNG:
  - `stages/stage_4_milti_agent/stage_4_graph.png`

---

### PHẦN 5: Distributed A2A System

**1. Kiến trúc hệ thống**

- Registry service chạy tại `10000`.
- Customer Agent chạy tại `10100`.
- Law Agent chạy tại `10101`.
- Tax Agent chạy tại `10102`.
- Compliance Agent chạy tại `10103`.

**2. Tên task trong registry**

- `legal_question` -> Law Agent
- `tax_question` -> Tax Agent
- `compliance_question` -> Compliance Agent

**3. Trace request flow**

- Request đi theo luồng:
  - `test_client.py`
  - Customer Agent
  - Registry discovery
  - Law Agent
  - Tax Agent và/hoặc Compliance Agent
  - Law Agent aggregate
  - Customer Agent trả kết quả về client
- Trong log, `trace_id` được truyền xuyên suốt qua metadata để theo dõi một request duy nhất qua nhiều agent.

**4. Cách propagate context**

- Ở `common/a2a_client.py`, metadata được gắn vào message:
  - `trace_id`
  - `context_id`
  - `delegation_depth`
- Điều này giúp debug request chain và kiểm soát độ sâu delegate.

**5. Phát hiện lỗi trả kết quả**

- Tôi đã cập nhật [test_client.py](test_client.py) để:
  - đọc `TaskStatus.message` khi task fail,
  - fallback sang `history` nếu cần,
  - hiển thị `task_state`.
- Nhờ đó client không còn chỉ in `No text response received` khi task đã có thông báo lỗi.

**6. Script khởi động Windows**

- Tôi đã thêm [start_all.ps1](start_all.ps1) để chạy toàn bộ system trên PowerShell Windows.

---

## PHẦN B: KẾT QUẢ THỰC HÀNH CÁC STAGES

### 1. Kết quả Stage 2

- Đã thêm:
  - `labor_law` vào `LEGAL_KNOWLEDGE`
  - tool `check_statute_of_limitations`
- Stage 2 chạy được với logic tool calling và knowledge grounding.

### 2. Kết quả Stage 3

- Đã cấu hình ReAct agent bằng `create_react_agent()`.
- Bật `debug=True` để xem chi tiết reasoning.
- Stage 3 chạy đúng luồng autonomous tool calling.

### 3. Kết quả Stage 4

- Đã thêm `privacy_agent`.
- Đã mở rộng routing để nhận diện privacy keywords.
- Đã render graph ra file PNG.

### 4. Kết quả Stage 5

- Hệ thống A2A chạy end-to-end:
  - Registry đăng ký agent thành công.
  - Customer Agent gọi Law Agent.
  - Law Agent gọi Tax/Compliance Agent qua registry.
  - Client nhận được response hoàn chỉnh.
- `test_client.py` đã được chỉnh để parse kết quả task tốt hơn.

---

## PHẦN C: CÂU HỎI ÔN TẬP

**1. Khi nào nên dùng single agent thay vì multi-agent?**

- Dùng single agent khi bài toán nhỏ, ít domain, không cần chạy song song, và ưu tiên đơn giản.
- Dùng multi-agent khi bài toán đa domain, cần specialist agents, cần scale và xử lý song song.

**2. Ưu điểm của A2A protocol so với gRPC hoặc REST thông thường?**

- A2A có khái niệm agent card, task, context, trace propagation và registry discovery, nên phù hợp hơn cho agent-to-agent collaboration.
- REST/gRPC là giao thức tổng quát; A2A được thiết kế riêng cho workflow giữa các agent.

**3. Làm thế nào để prevent infinite delegation loops trong A2A?**

- Giới hạn `delegation_depth`.
- Có `MAX_DELEGATION_DEPTH`.
- Có routing rules rõ ràng.
- Có timeout, logging và fallback.

**4. Tại sao cần Registry service? Có thể hardcode URLs không?**

- Registry giúp discovery động, dễ thay thế agent, dễ scale và tránh phụ thuộc URL cố định.
- Hardcode URLs chỉ phù hợp demo nhỏ, không phù hợp hệ thống nhiều agent.

---

## PHẦN D: NHẬN XÉT CHUNG

- Codelab đã giúp tôi đi qua 5 mức độ phát triển:
  - Direct LLM
  - LLM + Tools
  - ReAct Agent
  - Multi-Agent in-process
  - Distributed A2A system
- Phần quan trọng nhất của dự án này là:
  - phân tách trách nhiệm rõ ràng,
  - có routing và delegation,
  - có trace metadata,
  - có registry để discovery động,
  - và có thể mở rộng lên mô hình distributed.
