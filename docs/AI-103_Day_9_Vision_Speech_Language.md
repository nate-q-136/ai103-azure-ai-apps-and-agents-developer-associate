# AI-103 — Day 9: Azure AI Vision, Speech & Language (Chi tiết từng bước cấu hình SDK & Trọng tâm thi)

> **Mục tiêu:** Làm chủ toàn bộ các giải pháp **Computer Vision** (Image Analysis 4.0, Inpainting/Image generation, Alt-text cho Accessibility), **Speech Solutions** (STT, TTS, Diarization, SSML, Agent Voice interaction), và **Text Analysis** (Sentiment & Opinion Mining, PII Redaction, Extractive/Abstractive Summarization, Azure Translator) bám sát 100% mục tiêu thi AI-103.

**Thời lượng gợi ý:** 3–4 giờ.  
**Chi phí mục tiêu:** **$0.00** (Dùng gói Free Tier `F0` có sẵn cho từng dịch vụ trong `rg-ai103-lab`).  
**Phạm vi lab:** `rg-ai103-lab` → Azure AI Services multi-service resource.

---

## 1. Bản đồ Tổng quan Phân bổ Trọng số trong Đề thi AI-103

| Nhóm kỹ năng trong đề thi | Trọng số | Các dịch vụ cốt lõi |
| :--- | :--- | :--- |
| **Implement Computer Vision Solutions** | **10–15%** | Image Analysis 4.0, DALL-E 3 Image Generation, Inpainting/Edits, Custom Vision (Compact export), Alt-text. |
| **Implement Text Analysis Solutions** | **10–15%** | Azure AI Language (Sentiment, Opinion Mining, PII Redaction, Summarization), Azure AI Speech (STT, TTS, Diarization, SSML), Azure Translator. |

---

## 2. Hướng dẫn Từng bước: Azure AI Vision (Step-by-Step)

### 2.1 Image Analysis 4.0 (Python SDK)

Cài đặt SDK:
```bash
uv add azure-ai-vision-imageanalysis
```

Phân tích đa đặc trưng bằng `visual_features`:

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

ENDPOINT = os.getenv("VISION_ENDPOINT", "https://<your-vision>.cognitiveservices.azure.com/")
KEY = os.getenv("VISION_KEY", "<your-key>")

client = ImageAnalysisClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))

image_url = "https://learn.microsoft.com/azure/ai-services/computer-vision/media/quickstarts/presentation.png"

# Chỉ định rõ các tính năng cần phân tích để tối ưu chi phí
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[
        VisualFeatures.CAPTION,        # Sinh câu mô tả tổng quan
        VisualFeatures.DENSE_CAPTIONS,  # Mô tả từng khu vực trong ảnh
        VisualFeatures.TAGS,           # Nhãn từ khóa
        VisualFeatures.OBJECTS,        # Bounding boxes của vật thể
        VisualFeatures.READ,           # OCR đọc chữ
        VisualFeatures.SMART_CROPS     # Cắt khung hình thông minh
    ],
    smart_crops_aspect_ratios=[0.9, 1.33]  # Tỷ lệ khung hình mong muốn
)

# 1. Caption tổng quan
if result.caption:
    print(f"Caption: {result.caption.text} (Độ tự tin: {result.caption.confidence * 100:.1f}%)")

# 2. Bounding boxes vật thể
if result.objects:
    print("\nCác vật thể phát hiện:")
    for obj in result.objects.list:
        box = obj.bounding_box
        print(f" - {obj.tags[0].name} tại tọa độ [x={box.x}, y={box.y}, w={box.width}, h={box.height}]")

# 3. Smart Crops (Cắt ảnh thông minh giữ chủ thể)
if result.smart_crops:
    print("\nVùng Smart Crop gợi ý:")
    for crop in result.smart_crops.list:
        b = crop.bounding_box
        print(f" - Tỷ lệ {crop.aspect_ratio}: [x={b.x}, y={b.y}, w={b.width}, h={b.height}]")
```

---

### 2.2 Sinh Alt-Text Hỗ trợ Khả năng Tiếp cận (Accessibility Guidelines)
Đề thi AI-103 đặc biệt nhấn mạnh yêu cầu: **Sinh văn bản thay thế (Alt-Text) cho người khiếm thị tuân thủ chuẩn WCAG**:
- Dùng `VisualFeatures.CAPTION` để sinh câu mô tả ngắn gọn (dưới 125 ký tự).
- Kết hợp `VisualFeatures.READ` nếu bức ảnh có chứa văn bản hoặc biểu đồ số liệu quan trọng.

---

### 2.3 Image Generation & Editing (DALL-E 3 & Inpainting)
- **Prompt-driven generation:** Sinh ảnh từ mô tả văn bản qua Azure OpenAI DALL-E 3 deployment.
- **Inpainting (Mask-based edits):** Gửi một bức ảnh gốc kèm một **Mask Image** (ảnh mặt nạ nhị phân chỉ định vùng cần chỉnh sửa) và một prompt mới để AI chỉ vẽ lại đúng vùng được chỉ định mà giữ nguyên các khu vực còn lại.

---

## 3. Hướng dẫn Từng bước: Azure AI Speech (Step-by-Step)

### 3.1 Speech-to-Text (STT) & Speaker Diarization

Cài đặt SDK:
```bash
uv add azure-cognitiveservices-speech
```

Mã nguồn Python nhận diện giọng nói và phân đoạn người nói (Speaker Diarization):

```python
import time
import azure.cognitiveservices.speech as speechsdk

SPEECH_KEY = "<your-speech-key>"
SPEECH_REGION = "eastus"

speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
speech_config.speech_recognition_language = "vi-VN"

# Cấu hình âm thanh từ file WAV (16kHz, mono, PCM)
audio_config = speechsdk.audio.AudioConfig(filename="meeting-recording.wav")

# Sử dụng ConversationTranscriber để bật tính năng Speaker Diarization
transcriber = speechsdk.transcription.ConversationTranscriber(
    speech_config=speech_config,
    audio_config=audio_config
)

def handle_transcribed(evt):
    # evt.result.speaker_id: Nhận diện ai đang nói (Speaker 1, Speaker 2...)
    print(f"[{evt.result.speaker_id}]: {evt.result.text}")

transcriber.transcribed.connect(handle_transcribed)

# Bắt đầu nhận diện bất đồng bộ
transcriber.start_transcribing_async()
time.sleep(15)  # Chờ phiên nhận diện
transcriber.stop_transcribing_async()
```

---

### 3.2 Text-to-Speech (TTS) với Cú pháp SSML Chuẩn Đề thi

Mã nguồn Python phát giọng nói sử dụng **SSML** để tùy biến cao độ, tốc độ và phiên âm chuẩn quốc tế:

```python
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

ssml_payload = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="vi-VN">
  <voice name="vi-VN-NamMinhNeural">
    <prosody rate="+10%" pitch="+5%">
      Chào mừng bạn đến với kỳ thi AI-103.
    </prosody>
    <break time="500ms" />
    <prosody rate="-10%">
      Chúc bạn hoàn thành xuất sắc tất cả các câu hỏi thực hành!
    </prosody>
  </voice>
</speak>
"""

result = synthesizer.speak_ssml_async(ssml_payload).get()
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print(" Đã tổng hợp giọng nói qua SSML thành công!")
```

---

## 4. Hướng dẫn Từng bước: Azure AI Language (Step-by-Step)

### 4.1 PII Redaction & Opinion Mining (Khía cạnh chi tiết)

Cài đặt SDK:
```bash
uv add azure-ai-textanalytics
```

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

LANG_ENDPOINT = "https://<your-lang>.cognitiveservices.azure.com/"
LANG_KEY = "<your-key>"

client = TextAnalyticsClient(endpoint=LANG_ENDPOINT, credential=AzureKeyCredential(LANG_KEY))

text_samples = [
    "Khách sạn rất sạch sẽ nhưng đồ ăn sáng quá dở. Số CCCD của tôi là 001234567890."
]

# 1. Nhận diện và làm mờ PII
pii_response = client.recognize_pii_entities(text_samples, language="vi")
for doc in pii_response:
    print(f"Văn bản đã làm mờ PII: {doc.redacted_text}")
    for entity in doc.entities:
        print(f" - Phát hiện: {entity.text} ({entity.category}, độ tự tin: {entity.confidence_score * 100:.1f}%)")

# 2. Phân tích Sắc thái chi tiết từng khía cạnh (Opinion Mining)
sentiment_response = client.analyze_sentiment(text_samples, show_opinion_mining=True)
for doc in sentiment_response:
    print(f"\nCảm xúc chung: {doc.sentiment}")
    for sentence in doc.sentences:
        for opinion in sentence.mined_opinions:
            target = opinion.target
            print(f" Khía cạnh '{target.text}': {target.sentiment}")
            for assessment in opinion.assessments:
                print(f"   -> Từ cảm xúc bổ trợ: '{assessment.text}' ({assessment.sentiment})")
```

---

### 4.2 Text Summarization: Extractive vs Abstractive

Trong đề thi AI-103:
- **Extractive Summarization:** Trích xuất nguyên vẹn các câu quan trọng nhất có sẵn trong tài liệu. Rất phù hợp khi yêu cầu độ chính xác pháp lý (không sinh thêm từ ngữ ngoài văn bản gốc).
- **Abstractive Summarization:** Dùng mô hình ngôn ngữ sinh để diễn đạt lại nội dung tóm tắt bằng câu chữ mới, ngắn gọn và tự nhiên hơn.

---

## 5. Hướng dẫn Thao tác trên Bộ ba Studio UI (Vision, Speech & Language Studios)

Bộ ba giao diện Studio no-code của Azure giúp bạn kiểm thử nhanh chóng các mô hình và sinh code/SSML mẫu cho ứng dụng:

### 5.1 Vision Studio ([portal.vision.cognitive.azure.com](https://portal.vision.cognitive.azure.com))
1. **Kiểm thử Image Analysis 4.0:**
   - Đăng nhập Vision Studio, chọn resource trong `rg-ai103-lab`.
   - Chọn mục **Image analysis** $\rightarrow$ bấm thử:
     - *Add captions to images:* Xem câu mô tả tiếng Anh/Việt được AI tự động tạo.
     - *Detect common objects in images:* Xem bounding boxes màu vẽ trực tiếp lên vật thể.
     - *Extract common tags:* Xem danh sách nhãn từ khóa.
     - *Smart-crop images:* Chọn các tỷ lệ khung hình (1:1, 16:9, 4:3) để thấy AI tự động giữ chủ thể khuôn mặt ở trung tâm bức ảnh.
2. **Custom Vision Studio ([customvision.ai](https://www.customvision.ai)):**
   - Bấm **New Project**: Chọn **Classification** (Multiclass vs Multilabel) hoặc **Object Detection**.
   - Chọn **Domains:** Nếu cần tải model về máy chạy offline (Edge/IoT), bắt buộc chọn domain có chữ **(Compact)**.
   - Upload 15+ ảnh cho mỗi tag $\rightarrow$ bấm nút **Train** màu xanh $\rightarrow$ chọn **Quick Training**.
   - Sau khi train xong, bấm nút **Export** $\rightarrow$ chọn định dạng: `ONNX`, `TensorFlow Lite`, `Docker`.

---

### 5.2 Speech Studio ([speech.microsoft.com](https://speech.microsoft.com))
1. **Audio Content Creation (Soạn thảo SSML Trực quan):**
   - Truy cập Speech Studio $\rightarrow$ chọn **Audio Content Creation**.
   - Bấm **+ Create**: Nhập đoạn văn bản cần đọc.
   - Chọn giọng đọc: `vi-VN-NamMinhNeural` (giọng nam) hoặc `vi-VN-HoaiMyNeural` (giọng nữ).
   - Sử dụng thanh công cụ trực quan:
     - Bôi đen cụm từ $\rightarrow$ kéo thanh trượt **Speed (Tốc độ)** hoặc **Pitch (Cao độ)**.
     - Đặt con trỏ chuột giữa 2 câu $\rightarrow$ bấm nút **Insert pause** để chèn khoảng nghỉ (ví dụ: `500ms`).
   - Bấm nút **SSML** ở góc phải: Trình soạn thảo sẽ tự động xuất ra toàn bộ mã XML SSML chuẩn chỉnh để bạn copy thẳng vào code Python!

---

### 5.3 Language Studio ([language.cognitive.azure.com](https://language.cognitive.azure.com))
1. **Sentiment Analysis & Opinion Mining:**
   - Chọn thẻ **Classify text** $\rightarrow$ chọn **Analyze sentiment and mine opinions**.
   - Dán một câu review dịch vụ $\rightarrow$ bấm **Run**: Hệ thống hiển thị trực quan tỷ lệ phần trăm (Positive / Neutral / Negative) và liên kết từ chỉ khía cạnh với từ cảm xúc (ví dụ: `đồ ăn` $\rightarrow$ `dở`).
2. **PII Detection & Redaction:**
   - Chọn thẻ **Protect sensitive data** $\rightarrow$ chọn **Redact PII**.
   - Dán văn bản chứa số CCCD, thẻ ngân hàng $\rightarrow$ bấm **Run**: Hệ thống tự động làm mờ và hiển thị danh sách các thực thể nhạy cảm bị che giấu.

---

## 6. Kiến thức thi trọng tâm (Exam Objectives & Traps)

| Tình huống trong đề thi | Giải pháp / Lựa chọn chính xác |
| :--- | :--- |
| Cần cắt ảnh banner website sao cho khuôn mặt người luôn nằm ở trung tâm bức ảnh | Dùng **Image Analysis 4.0** với tính năng **Smart Crops** (`VisualFeatures.SMART_CROPS`). |
| Cần phân biệt rõ lời thoại của từng người trong cuộc họp thoại ghi âm nhiều người | Bật tính năng **Speaker Diarization** trong Azure AI Speech Service. |
| Khách hàng yêu cầu che toàn bộ số thẻ tín dụng và số CMND trong tin nhắn chăm sóc khách hàng | Sử dụng **Azure AI Language PII Detection & Redaction**. |
| Cần xuất mô hình thị giác máy tính chạy ngoại tuyến (Offline) trên thiết bị biên IoT / camera | Huấn luyện mô hình **Custom Vision** chọn domain **General (Compact)** và export sang định dạng ONNX/TensorFlow Lite. |
| Yêu cầu chatbot đọc tên các loại thuốc tây bằng tiếng Latinh chính xác theo phát âm quốc tế | Dùng thẻ **SSML `<phoneme>`** với bảng phiên âm quốc tế (IPA). |
| Cần phân tích phản hồi của khách hàng xem họ khen hay chê cụ thể những tính năng nào của sản phẩm | Dùng **Opinion Mining** (Aspect-based sentiment analysis) trong Azure AI Language. |

---

## 6. Definition of Done — Day 9

- [ ] Viết được code sử dụng Image Analysis 4.0 với các visual features (`caption`, `objects`, `smartCrops`).
- [ ] Hiểu rõ điều kiện để export Custom Vision chạy Offline (Compact domain).
- [ ] Viết được đoạn mã SSML chuẩn chỉnh có `<prosody>`, `<break>`, `<voice>`.
- [ ] Thực hiện được việc nhận diện PII và bóc tách Opinion Mining bằng Text Analytics SDK.
- [ ] Phân biệt được sự khác biệt giữa Extractive vs Abstractive Summarization.

---

## Sources (Official, checked 16/09/2026)

- [Azure AI Vision Image Analysis 4.0](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/overview-image-analysis)
- [Azure AI Speech Conversation Transcription (Diarization)](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/conversation-transcription)
- [Speech Synthesis Markup Language (SSML) Reference](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup)
- [Azure AI Language Sentiment Analysis & Opinion Mining](https://learn.microsoft.com/en-us/azure/ai-services/language-service/sentiment-opinion-mining/overview)
