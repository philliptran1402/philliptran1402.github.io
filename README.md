# philliptran1402.github.io

Landing page cá nhân, phục vụ tại **https://philliptran1402.github.io/**

Một file `index.html` tĩnh duy nhất — không build step, không framework, không dependency cài đặt.
Mở file bằng trình duyệt là thấy đúng y như bản chạy thật.

## Cách đưa lên mạng (lần đầu)

Repo **bắt buộc** phải tên chính xác `philliptran1402.github.io` thì GitHub mới phục vụ ở đường dẫn gốc
`https://philliptran1402.github.io/`. Đặt tên khác thì site sẽ nằm ở `/<tên-repo>/`.

```bash
cd philliptran1402.github.io
git init -b main
git add .
git commit -m "feat: personal landing page"
gh repo create philliptran1402.github.io --public --source=. --push
# hoặc tạo repo thủ công trên github.com rồi:
# git remote add origin https://github.com/philliptran1402/philliptran1402.github.io.git
# git push -u origin main
```

Sau khi push: vào **Settings → Pages**, mục *Build and deployment* chọn
**Source: Deploy from a branch**, branch `main`, thư mục `/ (root)` → Save.
Chờ khoảng 1–2 phút là site lên.

## Sửa nội dung

Mọi thứ nằm trong `index.html`:

| Cần sửa | Tìm tới |
|---|---|
| Tên, chức danh, địa điểm | thẻ `<header>` |
| Giới thiệu | `<section>` đầu tiên, mục *About* |
| Lĩnh vực | các `div.card` trong mục *What I work on* |
| Dự án | các `div.proj` trong mục *Selected work* |
| Stack | các `div.stack-row` |
| Liên hệ | thẻ `<footer>` |
| Màu sắc | khối `:root` trong `<style>` ở đầu file |

Ảnh đại diện lấy trực tiếp từ GitHub qua proxy `wsrv.nl` để bo tròn, nên đổi avatar trên GitHub
là trang này tự cập nhật theo — không cần sửa file.

## Ghi chú

- Ảnh preview khi chia sẻ link (LinkedIn/Slack) lấy từ thẻ `og:image`, hiện trỏ về avatar GitHub.
- Trang tôn trọng `prefers-reduced-motion`: tắt hiệu ứng nếu người dùng đặt chế độ giảm chuyển động.
- Phụ thuộc bên ngoài duy nhất: Google Fonts (Inter, JetBrains Mono) và `wsrv.nl` cho ảnh tròn.
  Cả hai đều có fallback — font rơi về system font, còn ảnh nếu muốn chắc chắn thì tự crop tròn
  rồi để `avatar.png` cạnh file này và đổi `src`.
