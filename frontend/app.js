(() => {
  const $ = (sel) => document.querySelector(sel);
  const baseUrlInput = $('#base_url');
  const rows = $('#rows');
  const createForm = $('#create-form');
  const createStatus = $('#create-status');
  const refreshBtn = $('#refresh');
  const depositForm = $('#deposit-form');
  const depositStatus = $('#deposit-status');
  const withdrawForm = $('#withdraw-form');
  const withdrawStatus = $('#withdraw-status');
  const transferForm = $('#transfer-form');
  const transferStatus = $('#transfer-status');
  const txnAccountInput = $('#txn_account_id');
  const loadTxnsBtn = $('#load-txns');
  const txnRows = $('#txn-rows');

  const api = {
    baseUrl() { return baseUrlInput.value.replace(/\/$/, ''); },
    async listAccounts() { const res = await fetch(`${this.baseUrl()}/accounts`); if (!res.ok) throw new Error(`List failed: ${res.status}`); return res.json(); },
    async createAccount(p) { const res = await fetch(`${this.baseUrl()}/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) }); const d = await res.json(); if (!res.ok) throw new Error(d?.detail || `Create failed`); return d; },
    async deleteAccount(id) { const res = await fetch(`${this.baseUrl()}/accounts/${id}`, { method: 'DELETE' }); if (!res.ok) throw new Error(`Delete failed`); return res.json(); },
    async deposit(p) { const res = await fetch(`${this.baseUrl()}/accounts/deposit`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) }); const d = await res.json(); if (!res.ok) throw new Error(d?.detail || `Deposit failed`); return d; },
    async withdraw(p) { const res = await fetch(`${this.baseUrl()}/accounts/withdraw`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) }); const d = await res.json(); if (!res.ok) throw new Error(d?.detail || `Withdraw failed`); return d; },
    async transfer(p) { const res = await fetch(`${this.baseUrl()}/accounts/transfer`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) }); const d = await res.json(); if (!res.ok) throw new Error(d?.detail || `Transfer failed`); return d; },
    async getTransactions(num) { const res = await fetch(`${this.baseUrl()}/accounts/${num}/transactions`); if (!res.ok) throw new Error(`Get txns failed`); return res.json(); }
  };

  function fmt(v) { return Number(v??0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function fmtDate(d) { return new Date(d).toLocaleString(); }

  async function refresh() {
    rows.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#888">Loading</td></tr>';
    try {
      const data = await api.listAccounts();
      if (!data.length) { rows.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#888">No accounts yet</td></tr>'; return; }
      rows.innerHTML = data.map(a => `<tr><td>${a.id}</td><td>${a.account_number}</td><td>${a.name}</td><td>${a.mobile_phone??''}</td><td>${fmt(a.balance)}</td><td>${fmtDate(a.account_created_on)}</td><td><button class="btn-delete" data-id="${a.id}">Delete</button></td></tr>`).join('');
      document.querySelectorAll('.btn-delete').forEach(btn => btn.addEventListener('click', handleDelete));
    } catch (e) { rows.innerHTML = `<tr><td colspan="7" class="err">${e.message}</td></tr>`; }
  }

  async function handleDelete(e) {
    const id = parseInt(e.target.dataset.id, 10);
    if (!confirm(`Delete account ${id}?`)) return;
    try { await api.deleteAccount(id); await refresh(); } catch (err) { alert(`Delete failed: ${err.message}`); }
  }

  async function loadTransactions() {
    const num = txnAccountInput.value.trim();
    if (!num) { txnRows.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#888">Enter account number</td></tr>'; return; }
    txnRows.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#888">Loading…</td></tr>';
    try {
      const txns = await api.getTransactions(num);
      if (!txns.length) { txnRows.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#888">No transactions</td></tr>'; return; }
      txnRows.innerHTML = txns.map(t => `<tr><td>${t.id}</td><td>${t.transaction_type}</td><td>${fmt(t.amount)}</td><td>${fmt(t.balance_before)}</td><td>${fmt(t.balance_after)}</td><td>${t.description||''}</td><td>${fmtDate(t.timestamp)}</td></tr>`).join('');
    } catch (e) { txnRows.innerHTML = `<tr><td colspan="7" class="err">${e.message}</td></tr>`; }
  }

  createForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const p = { account_number: $('#account_number').value.trim(), name: $('#name').value.trim(), mobile_phone: $('#mobile_phone').value.trim(), balance: Number($('#balance').value) };
    createStatus.className = ''; createStatus.textContent = 'Submitting';
    try { await api.createAccount(p); createStatus.className = 'ok'; createStatus.textContent = 'Created '; createForm.reset(); await refresh(); } catch (err) { createStatus.className = 'err'; createStatus.textContent = err.message || 'Error'; }
  });

  depositForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const p = { account_number: $('#deposit_account_id').value.trim(), amount: Number($('#deposit_amount').value) };
    depositStatus.className = ''; depositStatus.textContent = 'Processing…';
    try { await api.deposit(p); depositStatus.className = 'ok'; depositStatus.textContent = 'OK ✔'; depositForm.reset(); await refresh(); } catch (err) { depositStatus.className = 'err'; depositStatus.textContent = err.message; }
  });

  withdrawForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const p = { account_number: $('#withdraw_account_id').value.trim(), amount: Number($('#withdraw_amount').value) };
    withdrawStatus.className = ''; withdrawStatus.textContent = 'Processing…';
    try { await api.withdraw(p); withdrawStatus.className = 'ok'; withdrawStatus.textContent = 'OK ✔'; withdrawForm.reset(); await refresh(); } catch (err) { withdrawStatus.className = 'err'; withdrawStatus.textContent = err.message; }
  });

  transferForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const p = { from_account_number: $('#from_account_id').value.trim(), to_account_number: $('#to_account_id').value.trim(), amount: Number($('#transfer_amount').value) };
    transferStatus.className = ''; transferStatus.textContent = 'Processing…';
    try { await api.transfer(p); transferStatus.className = 'ok'; transferStatus.textContent = 'OK ✔'; transferForm.reset(); await refresh(); } catch (err) { transferStatus.className = 'err'; transferStatus.textContent = err.message; }
  });

  refreshBtn.addEventListener('click', refresh);
  loadTxnsBtn.addEventListener('click', loadTransactions);
  refresh();
})();
