# Douyin Auto-Sub Tool

Pipeline: tải video Douyin → làm mờ (một hoặc nhiều) vùng chọn trên video →
nhận diện giọng nói → dịch sang tiếng Việt (đúng thời điểm theo từng câu nói,
có thể dùng AI dịch theo ngữ cảnh cho mạch lạc) → chèn phụ đề dịch vào vùng đã
làm mờ → trộn nhạc nền (chỉnh âm lượng) → chèn logo (nếu có) → xuất video.

## Cài đặt

Yêu cầu: Python 3.10+, [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) đã có
trong PATH (đã xác nhận có sẵn trên máy này).

```powershell
pip install -r requirements.txt
```

Ghi chú:
- Engine **offline** (`faster-whisper`, `argostranslate`) phụ thuộc
  `ctranslate2`, vốn build native — nếu `pip install` lỗi trên Python bản
  mới (vd. 3.14), hãy tạo virtualenv với Python 3.11/3.12 chỉ cho phần này.
- Engine **api**/**ai** (`openai`, `deep-translator`) là pure-Python, luôn cài
  được. `GoogleTranslator` của `deep-translator` không cần API key. Whisper
  API và engine dịch **ai** thì cần `OPENAI_API_KEY`. Muốn dùng DeepL thay
  Google cho engine **api** thì set `DEEPL_API_KEY`.
- Desktop app (`pywebview`) dùng WebView2 runtime có sẵn trên Windows 11.
- Web app + desktop app: video/log của mỗi lần chạy được lưu trong
  `webapp_jobs/<job_id>/` (tự tạo khi chạy, không commit vào git).

## Lấy cookie Douyin

1. Đăng nhập douyin.com trên Chrome/Edge.
2. Cài extension "Get cookies.txt LOCALLY" (hoặc tương đương).
3. Export cookie của douyin.com ra file `cookies.txt` (định dạng Netscape).
4. Truyền đường dẫn file đó vào `--cookies`.

## Vùng làm mờ &amp; chèn phụ đề (`--blur-mode`)

Hai chế độ:

- **`auto` (mặc định trên web/desktop app)** — "phụ đề nói ở đâu, chữ ở đâu
  chèn ghép ở đó": với MỖI câu đã nhận diện giọng nói, tool tự trích 1 khung
  hình giữa câu đó, dùng OCR (`easyocr`) để tìm đúng vị trí chữ caption gốc
  trên màn hình tại thời điểm đó, rồi làm mờ + chèn phụ đề dịch ngay tại vị
  trí đó cho riêng câu đó — vị trí có thể thay đổi theo từng câu nếu caption
  gốc di chuyển. Không cần chọn vùng tay. Watermark/username cố định (thường ở
  góc trên) được bỏ qua tự động (chỉ ưu tiên vùng ở nửa dưới khung hình, nơi
  caption thường đặt). Nếu một câu không phát hiện được chữ (vd. khoảng lặng),
  tool dùng lại vị trí của câu liền trước.
- **`fixed`** — tọa độ `x,y,w,h` (pixel, gốc (0,0) ở góc trên-trái) tự chọn
  tay, **mỗi vùng có thể gắn riêng một mốc thời gian `start`/`end`** (giây) để
  chỉ áp dụng trong đúng khoảng đó — dùng khi caption gốc đổi vị trí giữa
  video (vd. vùng A từ 0-30s, vùng B từ 30s đến hết). Trên web/desktop app:
  tua video đến đoạn cần thiết rồi kéo chuột chọn vùng — vùng đó tự nhận thời
  điểm tua làm mốc bắt đầu và chạy đến hết video; tua tiếp đến đoạn khác rồi
  kéo vùng mới thì vùng trước tự kết thúc đúng lúc vùng mới bắt đầu (có thể
  sửa tay lại số giây trong danh sách vùng). Mỗi câu phụ đề tự bám theo vùng
  đang hiệu lực tại đúng thời điểm câu đó được nói. Nếu không chỉnh thời gian
  (qua `--blur-region` ở CLI, hoặc chỉ kéo một vùng duy nhất), vùng áp dụng
  cho toàn video như trước — có thể lặp lại `--blur-region` ở CLI để chọn
  nhiều vùng cùng lúc cho cả video (vùng đầu tiên dùng để chèn phụ đề, các
  vùng còn lại chỉ bị làm mờ). Nhanh hơn `auto` (không cần OCR) và không phụ
  thuộc độ chính xác nhận diện.

## Cài đặt API key &amp; cookie (mục &#9881; Cài đặt trên web/desktop app)

Bấm nút "⚙ Cài đặt" ở đầu trang để mở:
- **Provider AI** (chọn 1 để dùng cho engine dịch `ai`): OpenAI, Google Gemini
  hoặc Anthropic Claude — mỗi provider nhập API key riêng + chọn model, nhấn
  "🔍 Test" để gọi thử API thật và xác nhận key hợp lệ trước khi lưu.
- **Cookie Douyin** dùng chung cho mọi lần tải (dán nguyên nội dung
  `cookies.txt` hoặc chuỗi `name1=value1; name2=value2` lấy từ DevTools) —
  khỏi phải upload file mỗi lần ở Bước 1.

Bấm "Lưu cài đặt" để ghi lại. Dữ liệu lưu tại
`%USERPROFILE%\.douyin_auto_sub\settings.json` trên máy chạy server (không
nằm trong thư mục project, không bị commit nhầm vào git). API key hiển thị
lại dạng che (`sk-t***...CDEF`) sau khi lưu; để trống ô key khi lưu lần sau
nghĩa là giữ nguyên key cũ.

## Sử dụng

### Giao diện Web app

```powershell
python run_web.py
```

Tự mở browser tại `http://127.0.0.1:8765`. Giao diện cho phép:
1. Ở Bước 1, chọn một trong hai: dán link Douyin (+ cookie nếu cần), HOẶC
   chọn "Dùng video có sẵn trên máy" để nạp trực tiếp video đã tải từ trước
   (bỏ qua bước tải từ Douyin) — rồi bấm "Tiếp tục".
2. Kéo chuột trên khung hình video để chọn vùng làm mờ (tự tính toán đúng
   tọa độ pixel theo độ phân giải thật của video).
3. Chọn engine STT/dịch, nhạc nền (kèm thanh trượt âm lượng), logo + vị trí.
4. Bấm "Bắt đầu xử lý & xuất video", theo dõi log trực tiếp, rồi xem/tải
   video kết quả ngay trên trang.

Có thể dùng trên máy khác trong mạng LAN bằng cách đổi `HOST` trong
`run_web.py` thành `"0.0.0.0"` rồi truy cập `http://<ip-may-chay>:8765`.

### Giao diện Desktop app

```powershell
python run_desktop.py
```

Mở cùng giao diện trên trong một cửa sổ native (dùng WebView2 có sẵn trên
Windows 11, không cần cài Electron/Node). Không cần mở browser riêng.

Web app và desktop app dùng chung 100% logic backend
([webapp/server.py](webapp/server.py) +
[douyin_tool/pipeline.py](douyin_tool/pipeline.py)) — chỉ khác lớp hiển thị.

### Dòng lệnh (CLI)

```powershell
# Che do auto (OCR tu bam theo vi tri chu goc, khong can chon vung tay)
python run.py --url "https://www.douyin.com/video/xxxxx" `
  --cookies cookies.txt `
  --blur-mode auto `
  --stt-engine offline `
  --translate-engine api `
  --music nhac_nen.mp3 --music-volume 0.25 --voice-volume 1.0 `
  --tts-dub --tts-voice vi-VN-HoaiMyNeural --dub-volume 1.0 `
  --logo logo.png --logo-position top-right `
  --output-dir ./output

# Che do fixed (vung co dinh tu chon)
python run.py --url "https://www.douyin.com/video/xxxxx" `
  --blur-mode fixed --blur-region 40,1700,1000,180 `
  --output-dir ./output

# Dung video co san tren may (bo qua buoc tai Douyin) thay cho --url
python run.py --video-path "D:\videos\clip_da_tai.mp4" `
  --blur-mode auto `
  --output-dir ./output
```

Kết quả: `output/<id>_vi.mp4` (video cuối) và `output/<id>_vi.ass`
(file phụ đề đã dịch, giữ lại để kiểm tra/chỉnh sửa).

## Tham số chính

| Tham số | Ý nghĩa |
|---|---|
| `--url` / `--video-path` | bắt buộc chọn đúng một: `--url` để tải từ Douyin, hoặc `--video-path` để dùng video đã có sẵn trên máy (bỏ qua bước tải) |
| `--blur-mode` | `auto` (mặc định trên web/desktop — OCR tự bám vị trí chữ gốc theo từng câu) hoặc `fixed` (vùng cố định, cần `--blur-region`) |
| `--stt-engine` | `offline` (faster-whisper, chạy local) hoặc `api` (OpenAI Whisper) |
| `--translate-engine` | `api` (mặc định, Google Translate qua deep-translator — **miễn phí, không cần API key**, dịch từng câu riêng lẻ), `ai` (dịch cả transcript theo ngữ cảnh bằng provider/key cấu hình trong mục Cài đặt — mạch lạc/tự nhiên hơn nhưng cần API key trả phí) hoặc `offline` (argos-translate, local) |
| `--music-volume` / `--voice-volume` | hệ số âm lượng (0.0–1.0+) khi trộn nhạc nền với giọng gốc |
| `--tts-dub` | tự động đọc phụ đề tiếng Việt đã dịch bằng Edge-TTS, tự ghép theo mốc thời gian từng câu, trộn vào âm thanh video (cần Internet) |
| `--tts-voice` | giọng đọc Edge-TTS, ví dụ `vi-VN-HoaiMyNeural` (nữ, mặc định) hoặc `vi-VN-NamMinhNeural` (nam) |
| `--dub-volume` | hệ số âm lượng (0.0–1.0+) cho giọng lồng tiếng AI khi dùng `--tts-dub` |
| `--logo-position` | `top-left`/`top-right`/`bottom-left`/`bottom-right` hoặc `x,y` tùy chỉnh |
| `--keep-temp` | giữ file audio tạm để debug |

## Giới hạn hiện tại

- Chế độ `fixed`: mỗi vùng làm mờ là tọa độ cố định cho toàn bộ video (không
  tự động bám theo watermark di chuyển). Phụ đề dịch chỉ chèn vào vùng làm mờ
  đầu tiên; nếu chọn thêm vùng khác thì các vùng đó chỉ được làm mờ, không
  hiện chữ.
- Chế độ `auto`: nhận diện và làm mờ **tất cả** vùng chữ phát hiện được ở nửa
  dưới khung hình cho mỗi câu nói (tối đa 3 vùng); nếu không phát hiện được
  chữ nào thì không làm mờ gì cả. Vị trí chèn phụ đề dịch luôn theo vùng an
  toàn chuẩn theo tỉ lệ khung hình (9:16/1:1/4:5/16:9), không phụ thuộc vị trí
  chữ gốc. Độ chính xác phát hiện chữ phụ thuộc OCR — caption có hiệu ứng/màu
  sắc lạ có thể không phát hiện được. Chạy chậm hơn `fixed` vì phải trích
  xuất + chạy OCR cho từng câu nói, cộng thêm tải model OCR lần đầu (~vài
  trăm MB) và cài `easyocr` (kéo theo `torch`).
- `--tts-dub` (lồng tiếng AI bằng Edge-TTS): cần kết nối Internet (gọi dịch vụ
  Edge TTS của Microsoft, miễn phí, không cần API key). Mỗi câu được đọc rồi
  tăng tốc (nếu đọc dài hơn khoảng thời gian của câu) để khớp mốc thời gian
  phụ đề — với câu dịch quá dài so với thời lượng nói gốc, giọng đọc có thể
  hơi nhanh hơn bình thường để kịp đồng bộ.
- API key/cookie trong mục Cài đặt được lưu **dạng plaintext** tại
  `~/.douyin_auto_sub/settings.json` trên máy chạy server — phù hợp khi chạy
  local cho cá nhân; không deploy server này lên môi trường nhiều người dùng
  chung mà không thêm xác thực/mã hoá riêng.
- Engine dịch `ai` gọi 1 lần OpenAI cho toàn bộ transcript (để các câu dịch
  nhất quán, đúng ngữ cảnh) — cần `OPENAI_API_KEY` và tốn chi phí API tương
  ứng với độ dài transcript.
- Thời điểm hiện/ẩn từng dòng phụ đề lấy chính xác theo timestamp do
  Whisper trả về cho từng câu nói, không phải ước lượng.
- Cần cookie hợp lệ cho video riêng tư/yêu cầu đăng nhập; video public có thể
  tải không cần `--cookies`.
