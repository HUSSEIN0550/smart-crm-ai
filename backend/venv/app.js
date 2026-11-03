const API_URL = "http://127.0.0.1:8000";

const ticketForm = document.getElementById("ticketForm");
const ticketsContainer = document.getElementById("ticketsContainer");
const alertSound = document.getElementById("alertSound");

// دالة تحديث كروت الإحصائيات
async function fetchStats() {
    try {
        const response = await fetch(`${API_URL}/tickets/stats`);
        if (response.ok) {
            const stats = await response.json();
            document.getElementById("statTotal").innerText = stats.total;
            document.getElementById("statOpen").innerText = stats.open;
            document.getElementById("statClosed").innerText = stats.closed;
            document.getElementById("statUrgent").innerText = stats.urgent;
        }
    } catch (error) {
        console.error("تعذر جلب الإحصائيات:", error);
    }
}

async function fetchTickets() {
    try {
        const response = await fetch(`${API_URL}/tickets/`);
        const tickets = await response.json();

        // تحديث الإحصائيات
        fetchStats();

        if (tickets.length === 0) {
            ticketsContainer.innerHTML = `<p class="text-slate-500 text-center">لا توجد تذاكر مسجلة حالياً.</p>`;
            return;
        }

        ticketsContainer.innerHTML = tickets.map(ticket => {
            const ai = ticket.ai_analysis;
            const isClosed = ticket.status === "Closed";
            
            // التحقق مما إذا كانت التذكرة عاجلة/غاضبة ومفتوحة
            const isUrgent = ai && ai.sentiment.includes("عاجل") && !isClosed;

            return `
            <div class="p-4 rounded-lg border transition-all ${
                isUrgent 
                ? 'bg-rose-950/30 border-rose-500/80 shadow-lg shadow-rose-950/50 ring-1 ring-rose-500/40' 
                : 'bg-slate-700 border-slate-600'
            } space-y-3">
                <div class="flex justify-between items-start">
                    <div class="flex items-center gap-2">
                        <h3 class="font-bold text-lg ${isUrgent ? 'text-rose-300' : 'text-indigo-300'}">${ticket.title}</h3>
                        ${isUrgent ? `
                            <span class="animate-pulse bg-rose-600 text-white text-xs px-2 py-0.5 rounded-full font-bold">
                                ⚠️ أولوية قصوى
                            </span>
                        ` : ''}
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-1 text-xs rounded ${isClosed ? 'bg-emerald-900/50 text-emerald-300 border-emerald-600' : 'bg-slate-800 text-slate-300'} border">${ticket.status}</span>
                        ${!isClosed ? `
                            <button onclick="closeTicket(${ticket.id})" class="text-xs bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-1 rounded transition">
                                إغلاق التذكرة ✓
                            </button>
                        ` : ''}
                    </div>
                </div>
                <p class="text-slate-300 text-sm">${ticket.description}</p>
                
                ${ai ? `
                <div class="${isUrgent ? 'bg-rose-900/20 border-rose-500/30' : 'bg-slate-800 border-indigo-500/30'} p-3 rounded-lg border text-xs space-y-1.5">
                    <div class="flex gap-4">
                        <span class="${isUrgent ? 'text-rose-400 font-bold' : 'text-amber-400 font-semibold'}">المشاعر: ${ai.sentiment}</span>
                        <span class="text-emerald-400 font-semibold">التصنيف: ${ai.category}</span>
                    </div>
                    <p class="text-slate-300"><span class="text-indigo-400 font-medium">الرد المقترح:</span> ${ai.suggested_reply}</p>
                </div>
                ` : ''}

                <div class="text-xs text-slate-400 border-t border-slate-600/60 pt-2 flex justify-between">
                    <span>العميل: ${ticket.customer_email}</span>
                    <span>التاريخ: ${new Date(ticket.created_at).toLocaleString('ar-EG')}</span>
                </div>
            </div>
            `;
        }).join("");
    } catch (error) {
        ticketsContainer.innerHTML = `<p class="text-red-400 text-center">عذراً، تعذر الاتصال بالخادم الرئيسي (Backend).</p>`;
    }
}

async function closeTicket(ticketId) {
    try {
        const response = await fetch(`${API_URL}/tickets/${ticketId}/status?status=Closed`, {
            method: "PATCH"
        });
        if (response.ok) {
            fetchTickets();
        }
    } catch (error) {
        alert("تعذر تغيير حالة التذكرة.");
    }
}

ticketForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const title = document.getElementById("title").value;
    const customer_email = document.getElementById("email").value;
    const description = document.getElementById("description").value;

    try {
        const response = await fetch(`${API_URL}/tickets/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, customer_email, description })
        });

        if (response.ok) {
            ticketForm.reset();
            const createdTicket = await response.json();
            
            // تشغيل صوت التنبيه فوراً إذا كانت التذكرة الجديدة عاجلة
            if (createdTicket.ai_analysis && createdTicket.ai_analysis.sentiment.includes("عاجل")) {
                if (alertSound) alertSound.play().catch(() => {});
            }

            fetchTickets();
        } else {
            alert("حدث خطأ أثناء حفظ التذكرة.");
        }
    } catch (error) {
        alert("تعذر الاتصال بالسيرفر.");
    }
});

fetchTickets();