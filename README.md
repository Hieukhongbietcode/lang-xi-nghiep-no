# 🐺 Làng Xí Nghiệp Nợ — Bảng điều khiển Quản trò Ma Sói

Ứng dụng web **chỉ gồm một file** giúp Quản trò dẫn ván **Ma Sói** (theo luật Ultimate Werewolf và luật riêng của nhóm): chọn người chơi, xếp chỗ ngồi quanh bàn, thiết lập bộ bài, **chia bài ngay trên máy**, gọi vai từng đêm, tự xử lý luật sống/chết và theo dõi toàn bộ ván đấu.
Chạy trên điện thoại, iPad hay máy tính — **không cần cài đặt, không cần máy chủ, không cần tài khoản**.

<p align="center">
  <img src="docs/screenshots/01-trang-dau.png" width="19%" alt="Trang đầu">
  <img src="docs/screenshots/02-bo-bai.png" width="19%" alt="Thiết lập bộ bài">
  <img src="docs/screenshots/03-dem-vong-lang.png" width="19%" alt="Gọi vai trên vòng làng">
  <img src="docs/screenshots/04-bao-cao-dem.png" width="19%" alt="Báo cáo đêm">
  <img src="docs/screenshots/05-thao-luan.png" width="19%" alt="Thời gian thảo luận">
</p>

## 📑 Mục lục

- [Tính năng chính](#-tính-năng-chính)
- [Bắt đầu sử dụng](#-bắt-đầu-sử-dụng)
- [Hướng dẫn sử dụng chi tiết](HUONG-DAN-SU-DUNG.md)
- [Tuỳ chỉnh cho nhóm của bạn](#️-tuỳ-chỉnh-cho-nhóm-của-bạn)
- [Danh sách vai](#-danh-sách-vai)
- [Lưu ý](#️-lưu-ý)
- [Miễn trừ trách nhiệm](#-miễn-trừ-trách-nhiệm)
- [Giấy phép](#-giấy-phép)

## ✨ Tính năng chính

### Chuẩn bị ván

- **48 vai** chia 3 phe (Dân Làng · Sói · Thứ 3), mỗi vai có biểu tượng riêng, mô tả chức năng và điểm cân bằng.
- **Xếp chỗ ngồi** đúng vị trí quanh bàn; muốn đổi chỗ chỉ cần **chạm lần lượt 2 người**, hai ghế tự trượt đổi cho nhau.
- **Lưu bộ bài thường dùng** thành mẫu có tên, lần sau chạm 1 lần là nạp lại.
- **Hai cách chia bài:**
  - **Chia bài vật lý** — dùng lá bài thật như bình thường, Quản trò gọi từng vai dậy để ghi tên ở Đêm 1.
  - **Chia bài bằng app** — app tự xáo và chia. Mỗi người chạm vào tên mình → hiện lá **❓** → chạm vào lá để lật xem vai → bấm *"Tôi đã nhớ vai trò"* để úp lại và trả máy. Màu phe trên lá được để xám để người đứng cạnh không đoán được.

### Chống xem trộm khi chia bằng app

- Ô của người đã xem có viền **xanh lá**; xem từ lần thứ 2 trở đi chuyển **vàng** kèm *"Đã xem ×2"*.
- Chạm vào lá của người đã xem sẽ hiện cảnh báo trước khi cho xem lại.
- Trước khi bắt đầu Đêm 1, app liệt kê những ai đã xem nhiều lần và cho Quản trò chọn **chia bài lại** hoặc **vẫn bắt đầu**.

### Ban đêm

- **Gọi vai đúng thứ tự**, kiểm tra lựa chọn bắt buộc, có ghi chú riêng cho Quản trò, quay lại bước trước bất cứ lúc nào.
- Khi **chia bài bằng app**, app đã biết ai giữ vai gì nên **bỏ hết các bước gọi dậy chỉ để ghi tên**; Đêm 1 chỉ gọi những vai có chức năng. Các lời dặn cho phe Sói (Nanh Sói, Pháp Sư Sói, Sói Chiêm Bao) được gộp vào một bước.
- **Chơi trên vòng tròn chỗ ngồi:**
  - Người giữ vai đang được gọi sáng **viền theo phe** (xanh lá: Dân · đỏ: Sói · vàng: Thứ 3).
  - Chạm vào mặt người chơi để chọn mục tiêu, có mũi tên từ người giữ vai tới mục tiêu.
  - Giữ lâu vào một ghế để xem thông tin; thả tay vẫn hiện, chạm chỗ khác để đóng.
  - Sói chưa được phép dậy hiện hiệu ứng **zzz** đang ngủ.
- **Tự tìm người ngồi cạnh:**
  - **Chất Nhầy**: tự lấy người ngồi bên phải, có mũi tên, Quản trò chỉ bấm *Tiếp theo*.
  - **Ma Cà Rồng Thân Thiện**: điểm bắt đầu là người ngồi đối diện qua tâm bàn, có mũi tên chỉ hướng trái/phải.
  - **Thám Tử, Mất Ngủ, Kẻ Đánh Bom**: tự tính người ngồi cạnh.
- **Theo dõi phe phụ**: Trưởng Giáo Phái, Xác Sống, Chất Nhầy có ô liệt kê những ai đang cùng phe.
- **Con Ma** dậy cuối mỗi đêm và bắt buộc viết 1 chữ cái. Các chữ đã viết hiện ở màn Thảo luận, chạm để phóng to cho cả làng xem.

### Kết quả soi

- Kết quả soi (Tiên Tri, Tinh Thần Học, Pháp Sư Sói, Hào Quang, Bí Ẩn, Thám Tử, Mất Ngủ, Ma Cà Rồng…) **luôn được úp** dưới dạng tên người + lá **❓**.
- Chạm lần 1 để **phóng to**. Ở khung phóng to:
  - **Chạm đúng vào lá bài** thì lá mới lật ra kết quả.
  - Chạm chỗ khác hoặc nút ✕ thì thu nhỏ lại mà **không lật**. Quản trò chỉ nhầm người thì chọn lại được, không lộ kết quả.
- Có nút **lật màn hình 180°** để đưa máy cho người ngồi đối diện xem.

### Ban ngày và tổng kết

- Đồng hồ **Thảo luận / Biện minh** ngay giữa vòng làng; chạm vào ghế để chọn người bị treo cổ. Vòng làng tự co để **vừa một màn hình** iPad, không phải cuộn.
- **Báo cáo đêm** có hiệu ứng trời sáng và lật thẻ.
  - Nguyên nhân tử vong được che mờ, chỉ Quản trò chạm vào mới xem.
  - Người đã chết mang nhãn thời điểm chết (**Đ1** = Đêm 1, **N2** = Ngày 2).
- **Tự xử lý luật**: Cặp Đôi, Mẹ Trẻ, Sói Tuyết, Thợ Săn, Frankenstein / Nhân Bản thừa hưởng vai, Sói Con, Sói Đầu Đàn, Sói Trùm, Người Bệnh, Kẻ Bị Nguyền, Phù Thủy Già, Hoàng Tử, Già Làng… và kiểm tra thắng thua, kể cả các phe Thứ 3.
- **Nhật ký sự kiện, dòng thời gian và xuất PDF** tổng hợp ván đấu.
- Nhạc nền, hiệu ứng chuyển cảnh mượt, rung khi thao tác (trên máy hỗ trợ), giữ màn hình luôn sáng, **tự lưu ván** (tải lại trang vẫn chơi tiếp), hoàn tác nhiều bước.

## 🚀 Bắt đầu sử dụng

**Cách 1 — Mở trực tiếp trên máy:** tải file [`index.html`](index.html) về rồi mở bằng trình duyệt (Chrome, Safari, Edge…).

**Cách 2 — Mở trực tiếp qua web (GitHub Pages):**
Bấm vào link này: **https://hieukhongbietcode.github.io/lang-xi-nghiep-no/**

> 💡 Trên điện thoại / iPad: mở link rồi chọn **Thêm vào Màn hình chính** để dùng như một ứng dụng riêng lẻ.

Xem hướng dẫn từng bước trong **[HUONG-DAN-SU-DUNG.md](HUONG-DAN-SU-DUNG.md)**.

## 🛠️ Tuỳ chỉnh cho nhóm của bạn

Mọi thứ nằm trong file `index.html` (mở bằng trình soạn thảo văn bản bất kỳ):

| Muốn thay đổi | Tìm trong file |
|---|---|
| Danh sách người chơi có sẵn | `const OFFICE_MEMBERS = [...]` |
| Ảnh đại diện theo tên | `const STAFF_AVATARS = { "Allie": 'data:image/webp;base64,...' }` — ai không có ảnh sẽ dùng avatar 2 chữ cái đầu |
| Vai, mô tả, thứ tự gọi | `const ROLES_DB = [...]` |
| Điểm cân bằng của vai | `const ROLE_POINTS = {...}` |

Người chơi ngoài danh sách có thể thêm ngay trong ứng dụng (ô **New player**, hoặc gõ tên mới khi chọn ghế) — được nhớ trên máy cho các ván sau.

## 🃏 Danh sách vai

**Phe Dân Làng (30 vai):** Bảo Vệ, Con Ma, Dân Làng, Frankenstein, Già Làng, Hoàng Tử, Kẻ Bị Nguyền, Kẻ Si Tình, Kẻ Đánh Bom, Ma Cà Rồng Thân Thiện, Mất Ngủ, Mẹ Trẻ, Người Bệnh, Người Cứng Cỏi, Người Hoá Sói, Người Khám Phá, Người Phù Phép, Nhà Tinh Thần Học, Nữ Thợ Săn, Phù Thủy, Phù Thủy Già, Sinh Đôi, Thám Tử, Thầy Tu, Thị Trưởng, Thợ Săn, Tiên Tri, Tiên Tri Bí Ẩn, Tiên Tri Hào Quang, Tiên Tri Tập Sự

**Phe Sói (11 vai):** Ma Sói, Nanh Sói, Người Sói, Pháp Sư Sói, Sói Chiêm Bao, Sói Con, Sói Thiếu Niên, Sói Trùm, Sói Tuyết, Sói Ăn Chay, Sói Đầu Đàn

**Phe Thứ 3 (7 vai):** Chất Nhầy, Cupid, Du Côn, Nhân Bản, Thằng Ngốc, Trưởng Giáo Phái, Xác Sống

> Chạm vào biểu tượng của vai (ở màn Thiết lập bộ bài hoặc nút **i** khi chơi) để xem mô tả chi tiết và điểm cân bằng.

## ⚠️ Lưu ý

- **Luật nhà:** ứng dụng làm theo luật Ultimate Werewolf kết hợp **luật riêng của nhóm**. Một vài ví dụ:
  - Cặp Đôi được gọi dậy thảo luận mỗi đêm.
  - Người bị cấm túc không thể bị treo cổ.
  - Du Côn cướp phần thắng.
  - Già Làng chết vì bất kỳ lý do nào ngoài Sói cắn đều làm Dân Làng mất chức năng.
  - Tiên Tri Tập Sự chỉ được gọi từ Đêm 2.
  - Sói Đầu Đàn có thể biến Nanh Sói đang ngủ hoặc Pháp Sư Sói thành Ma Sói thường (mất chức năng cũ, từ đêm sau dậy cùng bầy).

  Nếu nhóm bạn chơi luật khác, hãy chỉnh trong `index.html` hoặc thống nhất trước khi chơi.
- **Chức năng Admin** (Sống / Chết, đổi vai) là công cụ sửa nhanh của Quản trò: **cố ý không** kích hoạt hiệu ứng dây chuyền (chết theo, thừa hưởng vai…) và không tự kiểm tra thắng thua.
- **Dữ liệu chỉ lưu trên máy đang dùng** (bộ nhớ trình duyệt). Đổi máy, đổi trình duyệt, dùng chế độ ẩn danh hoặc xoá dữ liệu trình duyệt sẽ mất những thứ sau:
  - ván đang chơi,
  - danh sách người chơi tự thêm,
  - các mẫu bộ bài đã lưu.
- **Cần mạng ở lần mở đầu tiên** để tải giao diện (Tailwind CSS, Font Awesome, phông chữ) và thư viện xuất PDF.
- **Nên mở trên trình duyệt mới** (Chrome, Safari, Edge bản gần đây). Rung khi thao tác / hết giờ không hoạt động trên iPhone (giới hạn của Safari).
- **Không để người chơi nhìn màn hình** khi Quản trò đang thao tác ban đêm — chỉ đưa máy khi đã phóng to kết quả cần cho người chơi xem.
- **Danh sách tên người chơi** trong file là tên thành viên của nhóm. Hãy cân nhắc trước khi để kho mã ở chế độ công khai (Public).

## 📢 Miễn trừ trách nhiệm

- *Ma Sói* / *Ultimate Werewolf* là trò chơi do **Bézier Games** phát hành. Làng Xí Nghiệp Nợ là **công cụ hỗ trợ Quản trò do cộng đồng tự làm**, **không** liên kết, **không** được tài trợ hay chứng nhận bởi nhà phát hành.
- Tên vai, mô tả luật và điểm cân bằng được viết lại / ước lượng phục vụ việc chơi trong nhóm, có thể khác với bản chính thức.
- Biểu tượng vai, logo và giao diện do nhóm tự thiết kế. Nhạc nền và âm thanh được nhúng sẵn chỉ dùng cho mục đích giải trí, phi thương mại.
- Phần mềm được cung cấp **"nguyên trạng"**, không kèm bất kỳ bảo đảm nào. Người dùng tự chịu trách nhiệm khi sử dụng; nhóm phát triển không chịu trách nhiệm cho bất kỳ thiệt hại hay tranh cãi nào phát sinh trong ván chơi. 🙂

## 🧱 Công nghệ

HTML + CSS + JavaScript thuần trong **một file**. Thư viện tải qua CDN: Tailwind CSS, Font Awesome, html2canvas + jsPDF (xuất PDF), Google Fonts. Nhạc nền và biểu tượng nhúng sẵn trong file; dữ liệu ván lưu bằng `localStorage` của trình duyệt — **không gửi dữ liệu đi đâu cả**.

## 📄 Giấy phép

Phát hành theo **Giấy phép MIT** — xem file [LICENSE](LICENSE).
