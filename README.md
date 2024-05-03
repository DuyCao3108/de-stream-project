# Giới thiệu project

> 2 **Video Demo** này có thể trình bày sơ lược về project trong trường hợp bạn không có nhu cầu tìm hiểu về chi tiết hoặc muốn xem demo luôn
> - **Demo 1 - streaming pipeline: [Video demo](https://record-project.s3.ap-southeast-2.amazonaws.com/demo1-done.mp4)**
> - **Demo 2 - batching pipeline: [Video demo](https://record-project.s3.ap-southeast-2.amazonaws.com/demo2-done.mp4)**

## Tóm tắt project
Project là một data pipeline xử lý được đồng thời dữ liệu stream và dữ liệu batch theo cấu trúc micro-services. Các công cụ thịnh hành hiện giờ trong xử lý big data được sử dụng, ví dụ như spark và kafka,... Dữ liệu đầu vào không có thực mà được giả lập.
## Diagram của Data pipeline
![Alt Text](https://record-project.s3.ap-southeast-2.amazonaws.com/gif-diagram.gif)

## Cấu trúc của Data pipline

Data pipeline này có thể được chia làm 3 phần chính.

### Phần tiếp nhận event: 
- **FastAPI Endpoint**: Cổng api của thư viện fastapi trong python, được kết nối với kafka producer. Khi data được gửi qua cổng /order thì kafka producer được trigger để truyền data đi tiếp.
- **Kafka Producer**: Kafka producer nhận event được truyền qua cổng api (user tạo order), sau đó thêm data vào 1 topic mà pyspark consumer đang subcribe.
- **PySpark Consumer**: Pyspark consumer subscribe topic của kafka và thực hiện hai tác vụ: gửi data vào datalake và gửi data vào nhánh streaming.
### Phần streaming:
- **PySpark Structured Streaming**: Pyspark sau khi nhận thấy có data mới trong topic sẽ thực hiện structured streaming. Consumer này sẽ lấy data về customer và product từ Postgres, gom các thông tin này vào cùng với order của customer và gửi vào Mongodb. Việc làm này là để document trong Mongodb chứa đủ các thông tin cần thiết, chứ không chỉ thông tin về order.
- **Streamlit Streaming Dashboard**: Dữ liệu thực sẽ được cập nhật trên dashboard của streamlit. Dashboard này chứa một số thông tin như: tổng sale, order, distinct customer hiện tại. Trendline của category sản phẩm. Order của bất kỳ customer cụ thể nào. Và cuối cùng là phần hiển thị những sản phẩm hiện có nhu cầu tăng đột biến.
- **Python Scheduled Process**: Để phát hiện các sản phẩm có nhu cầu tăng đột biến, một script python sẽ được schedule để thực hiện trong 1 khoảng thời gian (ở đây ví dụ là 1 ngày). Script này sẽ tổng hợp demand của tất cả sản phẩm được mua trong vòng 1 ngày qua và lưu trữ thông tin này trong một collection ở Mongodb. Sau đó, nó sẽ kiểm tra xem nhu cầu trong 1 ngày vừa qua có tăng đột biến so với những ngày trong quá khứ không. Tăng đột biến là khi demand lớn hơn 95 percentile của dữ liệu quá khứ sản phẩm đó. Nếu có sự tăng đột biến thì sẽ update lên dashboard streamlit.
### Phần batching:
- **AWS S3 as Data Lake**: Pyspark consumer tiếp nhận data và lập tức lưu trữ trong S3 như một data lake. 
- **Airflow Data Transfer DAG**: Sau một khoảng thời gian (ở đây ví dụ là 1 ngày), một Airflow DAG sẽ chạy để lấy dữ liệu từ S3 truyền vào Snowflake. Dữ liệu trong S3 có thể được data analyst, data scientist trích xuất để phân tích. Dữ liệu này chưa được transform nên đây là ELT pipeline.
- **Snowflake Data Warehouse**: Snowflake là một datawarehouse và có thể được dùng để thực hiện các dashboard phân tích dữ liệu quá khứ hay được trích xuất cho các phòng ban nếu cần.
### Micro-services:
Docker container được sử dụng trong đa số ứng dụng.
