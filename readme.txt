- Mỗi Agent tạo 1 thư mục riêng trong thư mục gym_splendorM/envs/agents (xem agent_A làm mẫu) có tên là <'Tên Agent'>
    Tất cả dữ liệu training cho bot của agent nào thì chỉ gói gọn trong thư mục của agent đó
    Ngoài ra trong thư mục riêng có 1 file bắt buộc là <'Tên Agent'>.py để import link của bot vào agent_interface

- Thay đổi đường dẫn vào bot theo dạng đã có trước tại file agent_interface.py tại thư mục gym_splendorM/envs/agents

- Các Agent cần có hàm reset kế thừa từ lớp cha Player, tất cả các thuộc tính của agent được khai báo thêm tại hàm này (xem agent_A làm mẫu)
    Nếu khai báo thuộc tính ở hàm khác thì rất có thể các thuộc tính sẽ không được reset sau mỗi trận đấu