from flask import Flask, request, url_for, jsonify, redirect, make_response
from html import escape
app = Flask(__name__)

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "Lop": "K47A",
        "scores": {
            "PMMNM": 8.5,
            "CSDL": 7.0,
            "MMT": 9.0
        }
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "Lop": "K47A",
        "scores": {
            "PMMNM": 6.0,
            "CSDL": 5.5,
            "MMT": 7.0
        }
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "Lop": "K47B",
        "scores": {
            "PMMNM": 9.5,
            "CSDL": 9.0
        }
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "Lop": "K47B",
        "scores": {
            "PMMNM": 4.0,
            "CSDL": 3.5,
            "MMT": 5.0
        }
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "Lop": "K47A",
        "scores": {}
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "Lop": "K47C",
        "scores": {
            "PMMNM": 7.5,
            "MMT": 8.0
        }
    }
}

def diem_tb(diem):
    if not diem:
        return None
    return sum(diem.values()) / len(diem)

def xep_loai(dtb):
    if dtb is None:
        return "--"
    if dtb >= 9:
        return "Xuất sắc"
    if dtb >= 8:
        return "Giỏi"
    if dtb >= 7:
        return "Khá"
    if dtb >= 5:
        return "Trung bình"
    return "Yếu"

def danh_sach():
    cac_lop = set()
    for sv in STUDENTS:
        t_tin = STUDENTS[sv]
        lop = t_tin["Lop"]
        cac_lop.add(lop)
    ket_qua = list(cac_lop)
    ket_qua.sort()
    return ket_qua

@app.route("/")
def index():
    total = len(STUDENTS)
    cac_lop = danh_sach()
    return f"""
    <h1>Quản lý sinh viên</h1>
    <p>Tổng số sinh viên: {total}</p>
    <p>Các lớp: {", ".join(cac_lop)}</p>
    <a href="/students">Danh sách sinh viên</a>
    <br>
    <a href="/api/students">API sinh viên</a>
    <br>
    <a href="/search">Tìm kiếm sinh viên</a>
    """

@app.route("/students")
def student_list():
    lop = request.args.get("Lop")
    students = STUDENTS

    if lop:
        students = {
            mssv: sv
            for mssv, sv in STUDENTS.items()
            if sv["Lop"].lower() == lop.lower()
        }

    cac_lop = danh_sach()
    filter_links = f"""<a href="{url_for('student_list')}">Tất cả</a>"""

    for lop_item in cac_lop:
        link = url_for("student_list", Lop=lop_item)
        filter_links += f""" | <a href="{link}">{lop_item}</a>"""

    rows = ""
    for mssv, sv in students.items():
        name = sv["name"]
        lop_sv = sv["Lop"]
        scores = sv["scores"]
        dtb = diem_tb(scores)
        loai = xep_loai(dtb)

        dtb_hien_thi = "--" if dtb is None else f"{dtb:.2f}"
        link = url_for("student_detail", mssv=mssv)

        rows += f"""
        <tr>
            <td><a href="{link}">{mssv}</a></td>
            <td>{name}</td>
            <td>{lop_sv}</td>
            <td>{dtb_hien_thi}</td>
            <td>{loai}</td>
        </tr>
        """

    if not students:
        rows = "<tr><td colspan='5'>Không có sinh viên phù hợp</td></tr>"

    return f"""
    <h1>Danh sách sinh viên</h1>
    <div>{filter_links}</div>
    <br>
    <table border="1">
        <tr>
            <th>MSSV</th>
            <th>Họ tên</th>
            <th>Lớp</th>
            <th>Điểm TB</th>
            <th>Xếp loại</th>
        </tr>
        {rows}
    </table>
    <br>
    <a href="/">Quay lại trang chủ</a>
    """ 

@app.route("/students/<mssv>")
def student_detail(mssv):
    sv = STUDENTS.get(mssv)
    if sv is None:
        return "Không tìm thấy sinh viên", 404

    name = sv["name"]
    lop = sv["Lop"]
    scores = sv["scores"]
    dtb = diem_tb(scores)
    loai = xep_loai(dtb)

    dtb_hien_thi = "--" if dtb is None else f"{dtb:.2f}"

    return f"""
    <h1>Chi tiết sinh viên</h1>
    <p>MSSV: {mssv}</p>
    <p>Họ tên: {name}</p>
    <p>Lớp: {lop}</p>
    <p>Điểm TB: {dtb_hien_thi}</p>
    <p>Xếp loại: {loai}</p>
    <a href="{url_for('export_scores', mssv=mssv)}">Tải bảng điểm (CSV)</a>
    <br><br>
    <a href="{url_for('student_list')}">Quay lại danh sách</a>
    """

@app.route("/api/students")
def api_students():
    return jsonify(STUDENTS)

@app.route("/sv/<mssv>")
def student_redirect(mssv):
    return redirect(url_for("student_detail", mssv=mssv)), 301

@app.route("/students/<mssv>/export")
def export_scores(mssv):
    sv = STUDENTS.get(mssv)
    if sv is None:
        return "Không tìm thấy sinh viên", 404

    scores = sv["scores"]
    csv_content = "hoc_phan,diem\n"
    for hoc_phan, diem in scores.items():
        csv_content += f"{hoc_phan},{diem}\n"

    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return response

@app.route("/search")
def search():
    q = request.args.get("q", "")
    keyword = q.lower()
    results = []

    if keyword:
        for mssv, sv in STUDENTS.items():
            name = sv["name"]
            if keyword in name.lower() or keyword in mssv.lower():
                results.append((mssv, sv))

    q_safe = escape(q)
    rows = ""

    for mssv, sv in results:
        rows += f"""
        <li>
            <a href="{url_for('student_detail', mssv=mssv)}">
                {escape(mssv)} - {escape(sv["name"])}
            </a>
        </li>
        """

    if not results and q:
        rows = "<p>Không tìm thấy sinh viên phù hợp.</p>"

    return f"""
    <h1>Tìm kiếm sinh viên</h1>
    <form method="get" action="/search">
        <input type="text" name="q" value="{q_safe}" placeholder="Nhập MSSV hoặc họ tên">
        <button type="submit">Tìm kiếm</button>
    </form>
    <h3>Kết quả tìm kiếm</h3>
    <ul>
        {rows}
    </ul>
    <br>
    <a href="/">Quay lại trang chủ</a>
    """

if __name__ == "__main__":
    app.run(debug=True, port=8000)
