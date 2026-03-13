// ==================== Helper Functions ====================
function updateDateTime() {
    const now = new Date();
    document.getElementById('currentDateTime').innerText = now.toLocaleDateString() + ' ' + now.toLocaleTimeString();
}
setInterval(updateDateTime, 1000);
updateDateTime();

function logout() {
    sessionStorage.removeItem('adminLoggedIn');
    window.location.href = '/';
}

// ==================== Sidebar Navigation ====================
document.querySelectorAll('.nav-item[data-page]').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const page = this.dataset.page;
        const pageMap = {
            'dashboard': '/admin-dashboard',
            'camera': '/camera-monitor',
            'employees': '/employees',
            'logs': '/attendance-logs',
            'analytics': '/analytics',
            'reports': '/reports',
            'settings': '/settings'
        };
        if (pageMap[page]) {
            window.location.href = pageMap[page];
        } else {
            console.warn('Unknown page:', page);
        }
    });
});

// ==================== Logout Buttons ====================
document.getElementById('logoutBtn').addEventListener('click', logout);
document.getElementById('headerLogoutBtn').addEventListener('click', logout);

// ==================== Quick Action Buttons ====================
document.getElementById('addEmployeeBtn').addEventListener('click', () => {
    window.location.href = '/employees?action=add';
});
document.getElementById('registerFaceBtn').addEventListener('click', () => {
    window.location.href = '/camera-monitor?mode=register';
});
document.getElementById('viewEmployeesBtn').addEventListener('click', () => {
    window.location.href = '/employees';
});

// ==================== Report Generation ====================
document.querySelectorAll('.report-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const type = this.dataset.type;
        alert(`Generating ${type} report... (backend integration needed)`);
    });
});

document.querySelectorAll('.report-export').forEach(btn => {
    btn.addEventListener('click', function() {
        const format = this.dataset.format;
        alert(`Exporting as ${format.toUpperCase()}... (backend integration needed)`);
    });
});

// ==================== Load Dashboard Data ====================
async function loadDashboardData() {
    try {
        const summaryRes = await fetch('/api/dashboard/summary');
        const summary = await summaryRes.json();

        document.getElementById('totalEmployees').innerText = summary.total_employees || 0;
        document.getElementById('presentToday').innerText = summary.present_today || 0;
        document.getElementById('absentToday').innerText = summary.absent_today || 0;
        document.getElementById('lateEntries').innerText = summary.late_entries || 0;

        document.getElementById('highestEmployee').innerText = summary.highest_attendance?._id || '-';
        document.getElementById('highestPercent').innerText = summary.highest_attendance?.count ? summary.highest_attendance.count + ' days' : '-';
        document.getElementById('lowestEmployee').innerText = summary.lowest_attendance?._id || '-';
        document.getElementById('lowestPercent').innerText = summary.lowest_attendance?.count ? summary.lowest_attendance.count + ' days' : '-';
        document.getElementById('avgAttendance').innerText = summary.attendance_percentage || '-';

        // Fetch today's attendance for recent activity
        const activityRes = await fetch('/api/attendance/today');
        const activity = await activityRes.json();

        const activityList = document.getElementById('activityList');
        activityList.innerHTML = '';
        if (Array.isArray(activity)) {
            activity.forEach(rec => {
                const badgeClass = rec.status === 'present' ? 'activity-badge' : (rec.status === 'late' ? 'activity-badge late' : 'activity-badge absent');
                activityList.innerHTML += `
                    <div class="activity-item">
                        <div class="activity-info">
                            <span>${rec.employee_name}</span>
                            <small>${rec.login_time || '--'}</small>
                        </div>
                        <div class="${badgeClass}">${rec.status}</div>
                    </div>
                `;
            });
        }

        // Update charts with monthly data
        if (summary.monthly_data && summary.monthly_data.length) {
            updateCharts(summary.monthly_data);
        }
    } catch (err) {
        console.error('Error loading dashboard data:', err);
    }
}

// ==================== Charts ====================
let dailyChart, weeklyChart;

function updateCharts(monthlyData) {
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const dailyCounts = monthlyData.slice(-7).map(d => d.count) || [40, 42, 38, 45, 44, 20, 0];
    if (dailyChart) {
        dailyChart.data.datasets[0].data = dailyCounts;
        dailyChart.update();
    } else {
        const ctxDaily = document.getElementById('dailyChart').getContext('2d');
        dailyChart = new Chart(ctxDaily, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Present',
                    data: dailyCounts,
                    backgroundColor: '#1e4a6f',
                    borderRadius: 6
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });
    }

    const weeklyLabels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
    const weeklyCounts = monthlyData.slice(-4).map(d => d.count) || [180, 195, 210, 200];
    if (weeklyChart) {
        weeklyChart.data.datasets[0].data = weeklyCounts;
        weeklyChart.update();
    } else {
        const ctxWeekly = document.getElementById('weeklyChart').getContext('2d');
        weeklyChart = new Chart(ctxWeekly, {
            type: 'line',
            data: {
                labels: weeklyLabels,
                datasets: [{
                    label: 'Attendance',
                    data: weeklyCounts,
                    borderColor: '#1e4a6f',
                    tension: 0.2,
                    fill: false
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}

// ==================== Camera Monitor ====================
const video = document.getElementById('cameraFeed');
const placeholder = document.getElementById('cameraPlaceholder');
const startBtn = document.getElementById('startCameraBtn');
const stopBtn = document.getElementById('stopCameraBtn');
const detectedName = document.getElementById('detectedName');
const detectedStatus = document.getElementById('detectedStatus');

let stream = null;
let recognitionInterval = null;

startBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = 'block';
        placeholder.style.display = 'none';
        recognitionInterval = setInterval(captureAndRecognize, 5000);
    } catch (err) {
        alert('Camera access denied: ' + err.message);
    }
});

stopBtn.addEventListener('click', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.style.display = 'none';
        placeholder.style.display = 'flex';
        if (recognitionInterval) clearInterval(recognitionInterval);
        detectedName.innerText = '-';
        detectedStatus.innerText = '-';
    }
});

function captureAndRecognize() {
    if (!stream) return;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const imageData = canvas.toDataURL('image/jpeg');

    fetch('/api/recognize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            detectedName.innerText = data.name;
            detectedStatus.innerText = data.message;
        } else {
            detectedName.innerText = 'Unknown';
            detectedStatus.innerText = data.message;
        }
    })
    .catch(err => {
        console.error('Recognition error:', err);
    });
}

// ==================== Initial Load ====================
loadDashboardData();