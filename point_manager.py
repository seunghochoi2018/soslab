import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class PointManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("포인트 지급 현황 관리 시스템")
        self.root.geometry("1200x700")
        
        # 데이터 파일
        self.data_file = "point_data.json"
        
        # 사용자 정보
        self.admins = {
            'admin1': 'admin123',
            'admin2': 'admin123'
        }
        
        self.current_user = None
        self.is_admin = False
        self.point_records = []
        self.filtered_records = []
        
        # 데이터 로드
        self.load_data()
        
        # UI 생성
        self.create_login_screen()
        
    def create_login_screen(self):
        """로그인 화면 생성"""
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(expand=True, fill='both')
        
        # 로그인 박스
        login_box = ttk.Frame(self.login_frame)
        login_box.place(relx=0.5, rely=0.5, anchor='center')
        
        # 제목
        title_label = ttk.Label(login_box, text="포인트 관리 시스템", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=20)
        
        # 접속 버튼들
        viewer_btn = ttk.Button(login_box, text="현황 조회하기", 
                               command=self.viewer_access, width=20)
        viewer_btn.pack(pady=10)
        
        admin_btn = ttk.Button(login_box, text="관리자 로그인", 
                              command=self.admin_login, width=20)
        admin_btn.pack(pady=5)
        
    def viewer_access(self):
        """조회자 접속"""
        self.current_user = "조회자"
        self.is_admin = False
        self.show_main_screen()
        
    def admin_login(self):
        """관리자 로그인"""
        login_window = tk.Toplevel(self.root)
        login_window.title("관리자 로그인")
        login_window.geometry("300x200")
        login_window.transient(self.root)
        login_window.grab_set()
        
        # 로그인 폼
        ttk.Label(login_window, text="관리자 ID:").pack(pady=5)
        username_entry = ttk.Entry(login_window, width=20)
        username_entry.pack(pady=5)
        
        ttk.Label(login_window, text="비밀번호:").pack(pady=5)
        password_entry = ttk.Entry(login_window, show="*", width=20)
        password_entry.pack(pady=5)
        
        def check_login():
            username = username_entry.get()
            password = password_entry.get()
            
            if username in self.admins and self.admins[username] == password:
                self.current_user = f"관리자 ({username})"
                self.is_admin = True
                login_window.destroy()
                self.show_main_screen()
            else:
                messagebox.showerror("로그인 실패", "ID 또는 비밀번호가 잘못되었습니다.")
        
        ttk.Button(login_window, text="로그인", command=check_login).pack(pady=10)
        ttk.Button(login_window, text="취소", command=login_window.destroy).pack(pady=5)
        
        username_entry.focus()
        password_entry.bind('<Return>', lambda e: check_login())
        
    def show_main_screen(self):
        """메인 화면 표시"""
        self.login_frame.destroy()
        
        # 메인 프레임
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 헤더
        self.create_header()
        
        # 관리자 패널 (관리자만)
        if self.is_admin:
            self.create_admin_panel()
        
        # 검색 패널
        self.create_search_panel()
        
        # 테이블
        self.create_table()
        
        # 통계 패널
        self.create_stats_panel()
        
        # 데이터 로드
        self.refresh_table()
        
    def create_header(self):
        """헤더 생성"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="포인트 지급 현황 관리", 
                 font=('Arial', 16, 'bold')).pack(side='left')
        
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side='right')
        
        ttk.Label(user_frame, text=f"접속자: {self.current_user}").pack(side='left', padx=5)
        ttk.Button(user_frame, text="로그아웃", command=self.logout).pack(side='left', padx=5)
        
    def create_admin_panel(self):
        """관리자 패널 생성"""
        admin_frame = ttk.LabelFrame(self.main_frame, text="포인트 기록 관리", padding=10)
        admin_frame.pack(fill='x', pady=(0, 10))
        
        # 입력 폼
        form_frame = ttk.Frame(admin_frame)
        form_frame.pack(fill='x')
        
        # 첫 번째 행
        row1 = ttk.Frame(form_frame)
        row1.pack(fill='x', pady=2)
        
        ttk.Label(row1, text="포인트 적립시기:", width=15).pack(side='left')
        self.accumulate_date = ttk.Entry(row1, width=12)
        self.accumulate_date.pack(side='left', padx=5)
        
        ttk.Label(row1, text="신청자:", width=10).pack(side='left', padx=(20, 0))
        self.applicant = ttk.Entry(row1, width=15)
        self.applicant.pack(side='left', padx=5)
        
        ttk.Label(row1, text="운송자:", width=10).pack(side='left', padx=(20, 0))
        self.transporter = ttk.Entry(row1, width=15)
        self.transporter.pack(side='left', padx=5)
        
        # 두 번째 행
        row2 = ttk.Frame(form_frame)
        row2.pack(fill='x', pady=2)
        
        ttk.Label(row2, text="신청자 적립금액:", width=15).pack(side='left')
        self.applicant_amount = ttk.Entry(row2, width=12)
        self.applicant_amount.pack(side='left', padx=5)
        
        ttk.Label(row2, text="운송자 적립금액:", width=15).pack(side='left', padx=(20, 0))
        self.transporter_amount = ttk.Entry(row2, width=12)
        self.transporter_amount.pack(side='left', padx=5)
        
        # 세 번째 행
        row3 = ttk.Frame(form_frame)
        row3.pack(fill='x', pady=2)
        
        ttk.Label(row3, text="포인트 지급시기:", width=15).pack(side='left')
        self.payment_date = ttk.Entry(row3, width=12)
        self.payment_date.pack(side='left', padx=5)
        
        ttk.Label(row3, text="과세시기:", width=10).pack(side='left', padx=(20, 0))
        self.tax_date = ttk.Entry(row3, width=12)
        self.tax_date.pack(side='left', padx=5)
        
        # 버튼 행
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=10)
        
        self.add_btn = ttk.Button(btn_frame, text="추가", command=self.add_record)
        self.add_btn.pack(side='left', padx=5)
        
        self.update_btn = ttk.Button(btn_frame, text="수정", command=self.update_record, state='disabled')
        self.update_btn.pack(side='left', padx=5)
        
        self.cancel_btn = ttk.Button(btn_frame, text="취소", command=self.cancel_edit, state='disabled')
        self.cancel_btn.pack(side='left', padx=5)
        
        self.editing_id = None
        
    def create_search_panel(self):
        """검색 패널 생성"""
        search_frame = ttk.LabelFrame(self.main_frame, text="검색 및 필터", padding=10)
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill='x')
        
        ttk.Label(search_row, text="검색:", width=8).pack(side='left')
        self.search_entry = ttk.Entry(search_row, width=20)
        self.search_entry.pack(side='left', padx=5)
        
        ttk.Label(search_row, text="시작일:", width=8).pack(side='left', padx=(20, 0))
        self.date_from = ttk.Entry(search_row, width=12)
        self.date_from.pack(side='left', padx=5)
        
        ttk.Label(search_row, text="종료일:", width=8).pack(side='left', padx=(20, 0))
        self.date_to = ttk.Entry(search_row, width=12)
        self.date_to.pack(side='left', padx=5)
        
        ttk.Button(search_row, text="검색", command=self.search_records).pack(side='left', padx=10)
        ttk.Button(search_row, text="초기화", command=self.reset_search).pack(side='left', padx=5)
        
        self.search_entry.bind('<Return>', lambda e: self.search_records())
        
    def create_table(self):
        """테이블 생성"""
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 테이블 헤더
        columns = ('번호', '포인트 적립시기', '신청자', '운송자', 
                  '신청자 적립금액', '운송자 적립금액', '포인트 지급시기', '과세시기')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # 컬럼 설정
        widths = [50, 120, 100, 100, 120, 120, 120, 120]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 관리자만 더블클릭으로 편집 가능
        if self.is_admin:
            self.tree.bind('<Double-1>', self.on_item_double_click)
            
        # 우클릭 메뉴 (관리자만)
        if self.is_admin:
            self.create_context_menu()
            
    def create_context_menu(self):
        """우클릭 컨텍스트 메뉴 생성"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="편집", command=self.edit_selected)
        self.context_menu.add_command(label="삭제", command=self.delete_selected)
        
        def show_context_menu(event):
            item = self.tree.selection()[0] if self.tree.selection() else None
            if item:
                self.context_menu.post(event.x_root, event.y_root)
        
        self.tree.bind('<Button-3>', show_context_menu)
        
    def create_stats_panel(self):
        """통계 패널 생성"""
        stats_frame = ttk.Frame(self.main_frame)
        stats_frame.pack(fill='x')
        
        # 통계 정보
        stat1 = ttk.LabelFrame(stats_frame, text="총 신청자 적립금액", padding=10)
        stat1.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.total_applicant_label = ttk.Label(stat1, text="0원", font=('Arial', 14, 'bold'))
        self.total_applicant_label.pack()
        
        stat2 = ttk.LabelFrame(stats_frame, text="총 운송자 적립금액", padding=10)
        stat2.pack(side='left', fill='x', expand=True, padx=5)
        self.total_transporter_label = ttk.Label(stat2, text="0원", font=('Arial', 14, 'bold'))
        self.total_transporter_label.pack()
        
        stat3 = ttk.LabelFrame(stats_frame, text="총 기록 수", padding=10)
        stat3.pack(side='left', fill='x', expand=True, padx=(5, 0))
        self.total_records_label = ttk.Label(stat3, text="0개", font=('Arial', 14, 'bold'))
        self.total_records_label.pack()
        
    def add_record(self):
        """기록 추가"""
        if not self.validate_form():
            return
            
        record = {
            'id': len(self.point_records) + 1,
            'accumulate_date': self.accumulate_date.get(),
            'applicant': self.applicant.get(),
            'transporter': self.transporter.get(),
            'applicant_amount': int(self.applicant_amount.get()),
            'transporter_amount': int(self.transporter_amount.get()),
            'payment_date': self.payment_date.get(),
            'tax_date': self.tax_date.get(),
            'created_at': datetime.now().isoformat()
        }
        
        self.point_records.append(record)
        self.save_data()
        self.refresh_table()
        self.clear_form()
        messagebox.showinfo("성공", "기록이 추가되었습니다.")
        
    def update_record(self):
        """기록 수정"""
        if not self.validate_form() or self.editing_id is None:
            return
            
        for record in self.point_records:
            if record['id'] == self.editing_id:
                record.update({
                    'accumulate_date': self.accumulate_date.get(),
                    'applicant': self.applicant.get(),
                    'transporter': self.transporter.get(),
                    'applicant_amount': int(self.applicant_amount.get()),
                    'transporter_amount': int(self.transporter_amount.get()),
                    'payment_date': self.payment_date.get(),
                    'tax_date': self.tax_date.get()
                })
                break
                
        self.save_data()
        self.refresh_table()
        self.cancel_edit()
        messagebox.showinfo("성공", "기록이 수정되었습니다.")
        
    def validate_form(self):
        """폼 유효성 검사"""
        if not all([self.accumulate_date.get(), self.applicant.get(), 
                   self.transporter.get(), self.applicant_amount.get(), 
                   self.transporter_amount.get()]):
            messagebox.showerror("입력 오류", "필수 항목을 모두 입력해주세요.")
            return False
            
        try:
            int(self.applicant_amount.get())
            int(self.transporter_amount.get())
        except ValueError:
            messagebox.showerror("입력 오류", "적립금액은 숫자만 입력 가능합니다.")
            return False
            
        return True
        
    def clear_form(self):
        """폼 초기화"""
        if hasattr(self, 'accumulate_date'):
            self.accumulate_date.delete(0, tk.END)
            self.applicant.delete(0, tk.END)
            self.transporter.delete(0, tk.END)
            self.applicant_amount.delete(0, tk.END)
            self.transporter_amount.delete(0, tk.END)
            self.payment_date.delete(0, tk.END)
            self.tax_date.delete(0, tk.END)
            
    def cancel_edit(self):
        """편집 취소"""
        self.editing_id = None
        self.clear_form()
        if hasattr(self, 'add_btn'):
            self.add_btn.config(state='normal')
            self.update_btn.config(state='disabled')
            self.cancel_btn.config(state='disabled')
            
    def on_item_double_click(self, event):
        """테이블 아이템 더블클릭"""
        self.edit_selected()
        
    def edit_selected(self):
        """선택된 항목 편집"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        record_id = int(item['values'][0])
        
        # 원본 데이터에서 찾기
        for record in self.point_records:
            if record['id'] == record_id:
                self.editing_id = record_id
                self.accumulate_date.delete(0, tk.END)
                self.accumulate_date.insert(0, record['accumulate_date'])
                self.applicant.delete(0, tk.END)
                self.applicant.insert(0, record['applicant'])
                self.transporter.delete(0, tk.END)
                self.transporter.insert(0, record['transporter'])
                self.applicant_amount.delete(0, tk.END)
                self.applicant_amount.insert(0, str(record['applicant_amount']))
                self.transporter_amount.delete(0, tk.END)
                self.transporter_amount.insert(0, str(record['transporter_amount']))
                self.payment_date.delete(0, tk.END)
                self.payment_date.insert(0, record['payment_date'])
                self.tax_date.delete(0, tk.END)
                self.tax_date.insert(0, record['tax_date'])
                
                self.add_btn.config(state='disabled')
                self.update_btn.config(state='normal')
                self.cancel_btn.config(state='normal')
                break
                
    def delete_selected(self):
        """선택된 항목 삭제"""
        selection = self.tree.selection()
        if not selection:
            return
            
        if messagebox.askyesno("삭제 확인", "선택한 기록을 삭제하시겠습니까?"):
            item = self.tree.item(selection[0])
            record_id = int(item['values'][0])
            
            self.point_records = [r for r in self.point_records if r['id'] != record_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("성공", "기록이 삭제되었습니다.")
            
    def search_records(self):
        """기록 검색"""
        search_term = self.search_entry.get().lower()
        date_from = self.date_from.get()
        date_to = self.date_to.get()
        
        filtered = []
        for record in self.point_records:
            # 텍스트 검색
            text_match = (not search_term or 
                         search_term in record['applicant'].lower() or
                         search_term in record['transporter'].lower())
            
            # 날짜 필터
            date_match = True
            if date_from and record['accumulate_date'] < date_from:
                date_match = False
            if date_to and record['accumulate_date'] > date_to:
                date_match = False
                
            if text_match and date_match:
                filtered.append(record)
                
        self.filtered_records = filtered
        self.refresh_table(use_filtered=True)
        
    def reset_search(self):
        """검색 초기화"""
        self.search_entry.delete(0, tk.END)
        self.date_from.delete(0, tk.END)
        self.date_to.delete(0, tk.END)
        self.filtered_records = []
        self.refresh_table()
        
    def refresh_table(self, use_filtered=False):
        """테이블 새로고침"""
        # 기존 데이터 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 데이터 로드
        records = self.filtered_records if use_filtered else self.point_records
        
        for i, record in enumerate(records, 1):
            values = (
                i,
                record['accumulate_date'],
                record['applicant'],
                record['transporter'],
                f"{record['applicant_amount']:,}원",
                f"{record['transporter_amount']:,}원",
                record['payment_date'] or '-',
                record['tax_date'] or '-'
            )
            self.tree.insert('', 'end', values=values)
            
        self.update_statistics()
        
    def update_statistics(self):
        """통계 업데이트"""
        records = self.filtered_records if self.filtered_records else self.point_records
        
        total_applicant = sum(r['applicant_amount'] for r in records)
        total_transporter = sum(r['transporter_amount'] for r in records)
        total_count = len(records)
        
        self.total_applicant_label.config(text=f"{total_applicant:,}원")
        self.total_transporter_label.config(text=f"{total_transporter:,}원")
        self.total_records_label.config(text=f"{total_count}개")
        
    def logout(self):
        """로그아웃"""
        self.main_frame.destroy()
        self.current_user = None
        self.is_admin = False
        self.create_login_screen()
        
    def load_data(self):
        """데이터 로드"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.point_records = json.load(f)
            except:
                self.point_records = self.get_sample_data()
        else:
            self.point_records = self.get_sample_data()
            self.save_data()
            
    def save_data(self):
        """데이터 저장"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.point_records, f, ensure_ascii=False, indent=2)
            
    def get_sample_data(self):
        """샘플 데이터"""
        return [
            {
                'id': 1,
                'accumulate_date': '2024-01-15',
                'applicant': '김철수',
                'transporter': '이영희',
                'applicant_amount': 50000,
                'transporter_amount': 30000,
                'payment_date': '2024-01-20',
                'tax_date': '2024-01-25',
                'created_at': '2024-01-15T09:00:00'
            },
            {
                'id': 2,
                'accumulate_date': '2024-01-18',
                'applicant': '박민수',
                'transporter': '정수진',
                'applicant_amount': 75000,
                'transporter_amount': 45000,
                'payment_date': '2024-01-23',
                'tax_date': '2024-01-28',
                'created_at': '2024-01-18T10:30:00'
            },
            {
                'id': 3,
                'accumulate_date': '2024-01-22',
                'applicant': '홍길동',
                'transporter': '김영수',
                'applicant_amount': 40000,
                'transporter_amount': 25000,
                'payment_date': '',
                'tax_date': '',
                'created_at': '2024-01-22T14:15:00'
            }
        ]
        
    def run(self):
        """프로그램 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PointManager()
    app.run()