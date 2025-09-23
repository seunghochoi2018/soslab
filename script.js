// 사용자 데이터 (실제 운영에서는 서버에서 관리)
const users = {
    'admin1': { password: 'admin123', role: 'admin', name: '관리자1' },
    'admin2': { password: 'admin123', role: 'admin', name: '관리자2' },
    'viewer1': { password: 'view123', role: 'viewer', name: '조회자1' },
    'viewer2': { password: 'view123', role: 'viewer', name: '조회자2' },
    'viewer3': { password: 'view123', role: 'viewer', name: '조회자3' }
};

// 포인트 데이터 저장소 (실제 운영에서는 데이터베이스)
let pointRecords = JSON.parse(localStorage.getItem('pointRecords')) || [];
let currentUser = null;
let editingId = null;

// DOM 요소들
const loginScreen = document.getElementById('loginScreen');
const mainScreen = document.getElementById('mainScreen');
const loginForm = document.getElementById('loginForm');
const pointForm = document.getElementById('pointForm');
const tableBody = document.getElementById('tableBody');
const currentUserSpan = document.getElementById('currentUser');
const userRoleSpan = document.getElementById('userRole');
const adminPanel = document.getElementById('adminPanel');

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadSampleData();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    // 접속 버튼들
    document.getElementById('viewerAccessBtn').addEventListener('click', handleViewerAccess);
    document.getElementById('adminAccessBtn').addEventListener('click', showAdminLogin);
    document.getElementById('cancelLoginBtn').addEventListener('click', hideAdminLogin);
    
    // 로그인 폼
    loginForm.addEventListener('submit', handleLogin);
    
    // 로그아웃
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    
    // 포인트 폼
    pointForm.addEventListener('submit', handlePointSubmit);
    document.getElementById('cancelBtn').addEventListener('click', cancelEdit);
    
    // 검색
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('resetBtn').addEventListener('click', resetSearch);
    document.getElementById('searchInput').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') performSearch();
    });
}

// 조회자 접속 처리
function handleViewerAccess() {
    currentUser = {
        username: 'viewer',
        role: 'viewer',
        name: '조회자'
    };
    showMainScreen();
}

// 관리자 로그인 폼 표시
function showAdminLogin() {
    document.querySelector('.access-options').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
}

// 관리자 로그인 폼 숨기기
function hideAdminLogin() {
    document.querySelector('.access-options').style.display = 'flex';
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

// 관리자 로그인 처리
function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (users[username] && users[username].password === password && users[username].role === 'admin') {
        currentUser = {
            username: username,
            ...users[username]
        };
        
        showMainScreen();
    } else {
        alert('관리자 ID 또는 비밀번호가 잘못되었습니다.');
    }
}

// 로그아웃 처리
function handleLogout() {
    currentUser = null;
    editingId = null;
    loginScreen.classList.add('active');
    mainScreen.classList.remove('active');
    
    // 초기 상태로 복원
    document.querySelector('.access-options').style.display = 'flex';
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

// 메인 화면 표시
function showMainScreen() {
    loginScreen.classList.remove('active');
    mainScreen.classList.add('active');
    
    currentUserSpan.textContent = currentUser.name;
    userRoleSpan.textContent = currentUser.role === 'admin' ? '관리자' : '조회자';
    
    // 관리자 권한에 따른 UI 조정
    const adminElements = document.querySelectorAll('.admin-only');
    adminElements.forEach(el => {
        el.style.display = currentUser.role === 'admin' ? 'block' : 'none';
    });
    
    loadPointRecords();
    updateStatistics();
}

// 포인트 기록 제출 처리
function handlePointSubmit(e) {
    e.preventDefault();
    
    if (currentUser.role !== 'admin') {
        alert('관리자만 데이터를 입력할 수 있습니다.');
        return;
    }
    
    const formData = new FormData(pointForm);
    const record = {
        id: editingId || Date.now(),
        accumulateDate: document.getElementById('accumulateDate').value,
        applicant: document.getElementById('applicant').value,
        transporter: document.getElementById('transporter').value,
        applicantAmount: parseInt(document.getElementById('applicantAmount').value),
        transporterAmount: parseInt(document.getElementById('transporterAmount').value),
        paymentDate: document.getElementById('paymentDate').value,
        taxDate: document.getElementById('taxDate').value,
        createdAt: editingId ? pointRecords.find(r => r.id === editingId).createdAt : new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    
    if (editingId) {
        // 수정
        const index = pointRecords.findIndex(r => r.id === editingId);
        pointRecords[index] = record;
        editingId = null;
        document.getElementById('submitBtn').textContent = '추가';
        document.getElementById('cancelBtn').style.display = 'none';
    } else {
        // 추가
        pointRecords.push(record);
    }
    
    saveToStorage();
    loadPointRecords();
    updateStatistics();
    pointForm.reset();
}

// 편집 취소
function cancelEdit() {
    editingId = null;
    pointForm.reset();
    document.getElementById('submitBtn').textContent = '추가';
    document.getElementById('cancelBtn').style.display = 'none';
}

// 기록 편집
function editRecord(id) {
    if (currentUser.role !== 'admin') return;
    
    const record = pointRecords.find(r => r.id === id);
    if (!record) return;
    
    editingId = id;
    document.getElementById('accumulateDate').value = record.accumulateDate;
    document.getElementById('applicant').value = record.applicant;
    document.getElementById('transporter').value = record.transporter;
    document.getElementById('applicantAmount').value = record.applicantAmount;
    document.getElementById('transporterAmount').value = record.transporterAmount;
    document.getElementById('paymentDate').value = record.paymentDate;
    document.getElementById('taxDate').value = record.taxDate;
    
    document.getElementById('submitBtn').textContent = '수정';
    document.getElementById('cancelBtn').style.display = 'inline-block';
    
    // 폼으로 스크롤
    adminPanel.scrollIntoView({ behavior: 'smooth' });
}

// 기록 삭제
function deleteRecord(id) {
    if (currentUser.role !== 'admin') return;
    
    if (confirm('이 기록을 삭제하시겠습니까?')) {
        pointRecords = pointRecords.filter(r => r.id !== id);
        saveToStorage();
        loadPointRecords();
        updateStatistics();
    }
}

// 포인트 기록 로드
function loadPointRecords(filteredRecords = null) {
    const records = filteredRecords || pointRecords;
    tableBody.innerHTML = '';
    
    records.forEach((record, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${formatDate(record.accumulateDate)}</td>
            <td>${record.applicant}</td>
            <td>${record.transporter}</td>
            <td>${formatNumber(record.applicantAmount)}</td>
            <td>${formatNumber(record.transporterAmount)}</td>
            <td>${formatDate(record.paymentDate)}</td>
            <td>${formatDate(record.taxDate)}</td>
            <td class="admin-only" style="display: ${currentUser?.role === 'admin' ? 'table-cell' : 'none'}">
                <button class="edit-btn" onclick="editRecord(${record.id})">수정</button>
                <button class="delete-btn" onclick="deleteRecord(${record.id})">삭제</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// 검색 수행
function performSearch() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    
    let filtered = pointRecords.filter(record => {
        const matchText = !searchTerm || 
            record.applicant.toLowerCase().includes(searchTerm) ||
            record.transporter.toLowerCase().includes(searchTerm);
        
        const matchDateFrom = !dateFrom || record.accumulateDate >= dateFrom;
        const matchDateTo = !dateTo || record.accumulateDate <= dateTo;
        
        return matchText && matchDateFrom && matchDateTo;
    });
    
    loadPointRecords(filtered);
}

// 검색 초기화
function resetSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    loadPointRecords();
}

// 통계 업데이트
function updateStatistics() {
    const totalApplicant = pointRecords.reduce((sum, record) => sum + record.applicantAmount, 0);
    const totalTransporter = pointRecords.reduce((sum, record) => sum + record.transporterAmount, 0);
    const totalRecords = pointRecords.length;
    
    document.getElementById('totalApplicantAmount').textContent = formatNumber(totalApplicant);
    document.getElementById('totalTransporterAmount').textContent = formatNumber(totalTransporter);
    document.getElementById('totalRecords').textContent = totalRecords;
}

// 로컬 스토리지에 저장
function saveToStorage() {
    localStorage.setItem('pointRecords', JSON.stringify(pointRecords));
}

// 샘플 데이터 로드 (처음 실행시에만)
function loadSampleData() {
    if (pointRecords.length === 0) {
        pointRecords = [
            {
                id: 1,
                accumulateDate: '2024-01-15',
                applicant: '김철수',
                transporter: '이영희',
                applicantAmount: 50000,
                transporterAmount: 30000,
                paymentDate: '2024-01-20',
                taxDate: '2024-01-25',
                createdAt: '2024-01-15T09:00:00.000Z',
                updatedAt: '2024-01-15T09:00:00.000Z'
            },
            {
                id: 2,
                accumulateDate: '2024-01-18',
                applicant: '박민수',
                transporter: '정수진',
                applicantAmount: 75000,
                transporterAmount: 45000,
                paymentDate: '2024-01-23',
                taxDate: '2024-01-28',
                createdAt: '2024-01-18T10:30:00.000Z',
                updatedAt: '2024-01-18T10:30:00.000Z'
            },
            {
                id: 3,
                accumulateDate: '2024-01-22',
                applicant: '홍길동',
                transporter: '김영수',
                applicantAmount: 40000,
                transporterAmount: 25000,
                paymentDate: '',
                taxDate: '',
                createdAt: '2024-01-22T14:15:00.000Z',
                updatedAt: '2024-01-22T14:15:00.000Z'
            }
        ];
        saveToStorage();
    }
}

// 유틸리티 함수들
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
}

function formatNumber(number) {
    return number.toLocaleString('ko-KR') + '원';
}