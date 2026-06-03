import asyncio
import random
import sys
import time
import threading
from datetime import datetime

from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QFont, QIcon, QTextCursor, QPalette, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox,
    QTextEdit, QGroupBox, QGridLayout, QProgressBar, QFrame,
    QCheckBox, QSplitter, QStatusBar, QToolButton, QSizePolicy,
    QMessageBox
)

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import os

load_dotenv()

# ─── THEMES ──────────────────────────────────────────────────────────────────

DARK_QSS = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 6px 10px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #89b4fa;
}
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 7px 18px;
    color: #cdd6f4;
    font-weight: 500;
}
QPushButton:hover { background-color: #45475a; }
QPushButton:pressed { background-color: #585b70; }
QPushButton#btnMulai {
    background-color: #a6e3a1;
    color: #1e1e2e;
    font-weight: bold;
    font-size: 14px;
}
QPushButton#btnMulai:hover { background-color: #94e2d5; }
QPushButton#btnMulai:disabled { background-color: #313244; color: #585b70; }
QPushButton#btnStop {
    background-color: #f38ba8;
    color: #1e1e2e;
    font-weight: bold;
    font-size: 14px;
}
QPushButton#btnStop:hover { background-color: #eba0ac; }
QPushButton#btnStop:disabled { background-color: #313244; color: #585b70; }
QTextEdit {
    background-color: #11111b;
    border: 1px solid #313244;
    border-radius: 8px;
    color: #cdd6f4;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 4px;
}
QProgressBar {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    height: 14px;
    text-align: center;
    color: #cdd6f4;
    font-size: 11px;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 5px;
}
QLabel#labelStat {
    font-size: 22px;
    font-weight: bold;
}
QFrame#separator {
    background-color: #313244;
}
QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #45475a;
    border-radius: 4px;
    background: #181825;
}
QCheckBox::indicator:checked {
    background: #89b4fa;
    border-color: #89b4fa;
}
QStatusBar { background-color: #181825; color: #6c7086; }
QToolButton {
    background: transparent;
    border: none;
    color: #6c7086;
    font-size: 16px;
    padding: 4px;
}
QToolButton:hover { color: #cdd6f4; }
"""

LIGHT_QSS = """
QMainWindow, QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-family: 'Segoe UI', Arial;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #ccd0da;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
    color: #1e66f5;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 6px 10px;
    color: #4c4f69;
    selection-background-color: #1e66f5;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #1e66f5;
}
QPushButton {
    background-color: #e6e9ef;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 7px 18px;
    color: #4c4f69;
    font-weight: 500;
}
QPushButton:hover { background-color: #dce0e8; }
QPushButton:pressed { background-color: #ccd0da; }
QPushButton#btnMulai {
    background-color: #40a02b;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
}
QPushButton#btnMulai:hover { background-color: #179299; }
QPushButton#btnMulai:disabled { background-color: #ccd0da; color: #9ca0b0; }
QPushButton#btnStop {
    background-color: #d20f39;
    color: #ffffff;
    font-weight: bold;
    font-size: 14px;
}
QPushButton#btnStop:hover { background-color: #e64553; }
QPushButton#btnStop:disabled { background-color: #ccd0da; color: #9ca0b0; }
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    color: #4c4f69;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 4px;
}
QProgressBar {
    background-color: #e6e9ef;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    height: 14px;
    text-align: center;
    color: #4c4f69;
    font-size: 11px;
}
QProgressBar::chunk {
    background-color: #1e66f5;
    border-radius: 5px;
}
QLabel#labelStat {
    font-size: 22px;
    font-weight: bold;
}
QFrame#separator {
    background-color: #ccd0da;
}
QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #ccd0da;
    border-radius: 4px;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #1e66f5;
    border-color: #1e66f5;
}
QStatusBar { background-color: #e6e9ef; color: #9ca0b0; }
QToolButton {
    background: transparent;
    border: none;
    color: #9ca0b0;
    font-size: 16px;
    padding: 4px;
}
QToolButton:hover { color: #4c4f69; }
"""

# ─── WORKER SIGNALS ───────────────────────────────────────────────────────────

class WorkerSignals(QObject):
    log_message   = Signal(str, str)   # (pesan, tipe: info/ok/warn/err)
    stat_update   = Signal(int, int)       # approve, skip
    progress      = Signal(int, int)   # current, total
    status_bar    = Signal(str)
    finished      = Signal()
    started       = Signal()


# ─── ASYNC WORKER ─────────────────────────────────────────────────────────────

class FasihWorker:
    def __init__(self, config: dict, signals: WorkerSignals):
        self.config  = config
        self.signals = signals
        self._stop   = False

        self.counter_approve  = 0
        self.counter_skip     = 0

        # Progress tracking: diupdate realtime per ID selesai
        self._progress_current = 0
        self._progress_total   = 0

    def stop(self):
        self._stop = True

    def log(self, msg, tipe="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.signals.log_message.emit(f"[{ts}] {msg}", tipe)

    def jeda(self, mn=None, mx=None):
        mn = mn or self.config["jeda_min"]
        mx = mx or self.config["jeda_max"]
        return asyncio.sleep(random.uniform(mn, mx))

    def _catat_outcome(self, outcome: str):
        """Catat outcome ID (approve/skip/error) dan emit stat + progress."""
        if outcome == "approve":
            self.counter_approve += 1
        elif outcome in ("skip", "error"):
            self.counter_skip += 1
        self.signals.stat_update.emit(
            self.counter_approve, self.counter_skip
        )
        # Progress naik +1 setiap ID selesai apapun hasilnya
        self._progress_current += 1
        self.signals.progress.emit(self._progress_current, self._progress_total)

    # ── Login & navigasi ──────────────────────────────────────────────────────
    async def login_dan_navigasi(self, page):
        self.log("Membuka halaman utama...")
        await page.goto("https://fasih-sm.bps.go.id", wait_until="domcontentloaded", timeout=60_000) #revisi
        await self.jeda()

        self.log("Klik Login SSO BPS...")
        await page.click('a[href="/oauth2/authorization/ics"]')
        await page.wait_for_load_state("load")
        await self.jeda()

        self.log("Mengisi username...")
        await page.fill('#username', self.config["username"])
        await self.jeda(0.8, 1.5)

        self.log("Mengisi password...")
        await page.fill('#password', self.config["password"])
        await self.jeda(0.8, 1.5)

        self.log("Klik Log In...")
        await page.click('#kc-login')
        await page.wait_for_load_state("load")
        await self.jeda()

        self.log("Klik link survei...")
        await page.click('a[href*="/survey-collection/general/8712a6fc-a996-4a8f-ad6f-56a278c19288"]')
        await page.wait_for_load_state("load")
        await self.jeda()

        self.log("Klik tab Data...")
        await page.click('a[href="/survey-collection/collect/8712a6fc-a996-4a8f-ad6f-56a278c19288"]')
        await page.wait_for_load_state("load")
        await self.jeda()

        self.log("Klik tombol SUBMITTED BY Pencacah...")
        await page.click('button.btn-outline-primary:has-text("SUBMITTED BY Pencacah")')
        await self.jeda()

        self.log("Menunggu tabel ID muncul...")
        await page.wait_for_selector(
            'td a[href*="assignment-detail"]',
            timeout=self.config["timeout_tabel"]
        )
        await self.jeda()
        self.log("Login dan navigasi selesai.", "ok")

    # ── Pastikan filter aktif ─────────────────────────────────────────────────
    async def pastikan_filter_submitted(self, page):
        try:
            tombol = await page.wait_for_selector(
                'button.btn-outline-primary:has-text("SUBMITTED BY Pencacah")',
                timeout=5_000
            )
            kelas = await tombol.get_attribute("class")
            if "active" not in (kelas or ""):
                self.log("Filter SUBMITTED tidak aktif, klik ulang...", "warn")
                await tombol.click()
                await self.jeda()
            await page.wait_for_selector(
                'td a[href*="assignment-detail"]',
                timeout=self.config["timeout_tabel"]
            )
        except PlaywrightTimeout:
            pass

    # ── Ambil semua link ──────────────────────────────────────────────────────
    async def ambil_semua_link(self, page):
        await page.wait_for_selector(
            'td a[href*="assignment-detail"]',
            timeout=self.config["timeout_tabel"]
        )
        links = await page.query_selector_all('td a[href*="assignment-detail"]')
        result = []
        for link in links:
            href = await link.get_attribute("href")
            teks = (await link.inner_text()).strip()
            if href:
                full_url = (
                    f"https://fasih-sm.bps.go.id{href}"
                    if href.startswith("/") else href
                )
                result.append({"url": full_url, "teks": teks})
        return result

    # ── Cek status terakhir ───────────────────────────────────────────────────
    async def get_status_terakhir(self, page):
        try:
            await page.wait_for_selector(
                "#datatable tbody tr.ng-star-inserted", timeout=8_000
            )
            baris = await page.query_selector_all("#datatable tbody tr.ng-star-inserted")
            if not baris:
                return None
            tds = await baris[-1].query_selector_all("td")
            if len(tds) < 2:
                return None
            teks = (await tds[1].inner_text()).strip().upper()
            if "SUBMITTED" in teks: return "SUBMITTED"
            if "APPROVED"  in teks: return "APPROVED"
            if "REJECTED"  in teks: return "REJECTED"
            return None
        except PlaywrightTimeout:
            return None

    # ── Fase 1: cek status + klik Review ─────────────────────────────────────
    # Return: "lanjut" | "skip:<alasan>" | "error:<alasan>"
    async def fase1_review(self, tab, teks):
        try:
            await tab.goto(tab._url_detail, wait_until="domcontentloaded")
            await self.jeda()

            status = await self.get_status_terakhir(tab)
            if status in ("APPROVED", "REJECTED"):
                self.log(f"  ⏭ [{teks}] Skip — status {status}", "warn")
                return f"skip:status_{status.lower()}"
            if status == "SUBMITTED":
                self.log(f"  [{teks}] Status SUBMITTED, lanjut...")
            else:
                self.log(f"  ⚠️ [{teks}] Status tidak terbaca, tetap lanjut...", "warn")

            tombol_review = None
            for percobaan in range(1, 3):
                try:
                    tombol_review = await tab.wait_for_selector(
                        "a.btn.btn-primary:has-text('Review')",
                        timeout=self.config["timeout_review"]
                    )
                    break
                except PlaywrightTimeout:
                    if percobaan == 1:
                        self.log(f"  ⚠️ [{teks}] Tombol Review tidak muncul, reload...", "warn")
                        await tab.reload(wait_until="domcontentloaded")
                        await self.jeda()
                    else:
                        self.log(f"  ❌ [{teks}] Tombol Review tetap tidak muncul.", "err")
                        return "error:tombol_review"

            await tab.bring_to_front()
            await self.jeda(0.8, 1.5)
            await tombol_review.click()
            self.log(f"  [{teks}] Klik Review ✓", "ok")
            return "lanjut"

        except Exception as e:
            self.log(f"  ❌ [{teks}] Error fase 1: {e}", "err")
            return "error:exception_fase1"

# ── Fase 2: Approve + Ya ──────────────────────────────────────────────────
    # Return: "approve" | "skip:<alasan>" | "error:<alasan>"
    async def fase2_approve(self, tab, teks):
        try:
            # LANGSUNG TUNGGU TOMBOL APPROVE MUNCUL (Bukan nunggu h1 lagi)
            tombol_approve = None
            for percobaan in range(1, 3):
                try:
                    tombol_approve = await tab.wait_for_selector(
                        "#buttonApprove", 
                        timeout=self.config["timeout_review"] # pakai timeout_review yg lebih masuk akal
                    )
                    break
                except PlaywrightTimeout:
                    if percobaan == 1:
                        self.log(f"  ⚠️ [{teks}] Tombol Approve belum muncul, refresh halaman...", "warn")
                        await tab.reload(wait_until="domcontentloaded")
                        await self.jeda()
                    else:
                        self.log(f"  ❌ [{teks}] Tombol Approve tetap tidak ditemukan setelah reload.", "err")
                        return "error:tombol_approve"

            await tab.bring_to_front()
            await self.jeda(0.8, 1.2)
            self.log(f"  [{teks}] Klik Approve...")
            await tombol_approve.click()

            # Tunggu Dialog Konfirmasi 'Ya' muncul
            try:
                tombol_ya = await tab.wait_for_selector(
                    "button.swal2-confirm",
                    timeout=self.config["timeout_popup"]
                )
            except PlaywrightTimeout:
                self.log(f"  ❌ [{teks}] Dialog Ya tidak muncul.", "err")
                return "error:dialog_ya"

            await tab.bring_to_front()
            await self.jeda(0.8, 1.2)
            self.log(f"  [{teks}] Klik Ya...")
            await tombol_ya.click()

            # Tunggu respon popup hasil sukses/gagal
            try:
                await tab.wait_for_selector(
                    "#swal2-html-container",
                    timeout=self.config["timeout_popup"]
                )
                teks_popup = (await tab.inner_text("#swal2-html-container")).strip().lower()

                if "success" in teks_popup or "berhasil" in teks_popup:
                    self.log(
                        f"  ({self.counter_approve + 1}) ✅ [{teks}] Berhasil di-approve!", "ok"
                    )
                    return "approve"
                elif "error" in teks_popup or "gagal" in teks_popup:
                    self.log(f"  ⏭ [{teks}] Skip — server menolak approve (popup error).", "warn")
                    return "skip:popup_error"
                else:
                    self.log(f"  ⚠️ [{teks}] Popup tidak dikenali: '{teks_popup}'", "warn")
                    return "error:popup_tidak_dikenali"

            except PlaywrightTimeout:
                self.log(f"  ❌ [{teks}] Popup hasil tidak muncul.", "err")
                return "error:popup_tidak_muncul"

        except Exception as e:
            self.log(f"  ❌ [{teks}] Error fase 2: {e}", "err")
            return "error:exception_fase2"

        finally:
            await tab.close()
            self.log(f"  Tab [{teks}] ditutup.")
            
    # ── Proses satu batch ─────────────────────────────────────────────────────
    async def proses_batch(self, context, batch, idx_batch, total_batch):
        self.log(f"\n  == Batch {idx_batch}/{total_batch}: {len(batch)} ID ==")
        self.signals.status_bar.emit(
            f"Batch {idx_batch}/{total_batch} — membuka {len(batch)} tab..."
        )

        tabs = []
        for id_info in batch:
            if self._stop:
                break
            tab = await context.new_page()
            tab._url_detail = id_info["url"]
            tab._teks       = id_info["teks"]
            tabs.append(tab)
            self.log(f"  Tab dibuka: {id_info['teks']}")
            await asyncio.sleep(0.3)

        # Fase 1 — outcome per tab dicatat di sini jika langsung selesai
        self.log(f"\n  [Fase 1] Cek status & klik Review...")
        tabs_siap = []  # list of (tab, teks) yang lolos ke fase 2
        for tab in tabs:
            if self._stop:
                await tab.close()
                continue
            teks = tab._teks
            hasil_f1 = await self.fase1_review(tab, teks)

            if hasil_f1 == "lanjut":
                tabs_siap.append(tab)
            else:
                # outcome sudah final di fase 1
                await tab.close()
                self.log(f"  Tab [{teks}] ditutup (fase 1).")
                kategori = hasil_f1.split(":")[0]  # "skip" atau "error"
                self._catat_outcome(kategori)

        if not tabs_siap:
            self.log("  Tidak ada tab yang lolos fase 1.", "warn")
            return

        # Fase 2 — outcome final ditentukan di sini
        self.log(f"\n  [Fase 2] Approve {len(tabs_siap)} tab...")
        for tab in tabs_siap:
            if self._stop:
                await tab.close()
                self.log(f"  Tab [{tab._teks}] ditutup (dihentikan).")
                continue
            hasil_f2 = await self.fase2_approve(tab, tab._teks)
            kategori = hasil_f2.split(":")[0]  # "approve", "skip", atau "error"
            self._catat_outcome(kategori)
            await self.jeda(1.0, 2.0)

    # ── Loop utama ────────────────────────────────────────────────────────────
    async def run(self):
        self.signals.started.emit()
        self.signals.status_bar.emit("Memulai browser...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.config["headless"],
                slow_mo=200,
                args=["--start-maximized"]
            )
            context = await browser.new_context(
                viewport=None,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )

            tab_list = await context.new_page()
            try:
                await self.login_dan_navigasi(tab_list)
            except Exception as e:
                self.log(f"❌ Gagal login: {e}", "err")
                await browser.close()
                self.signals.finished.emit()
                return

            sudah_diproses = set()
            putaran        = 0

            while not self._stop:
                putaran += 1
                self.log(f"\n─── Putaran {putaran} ───────────────────────────────")
                self.signals.status_bar.emit(f"Putaran {putaran} — mengambil data tabel...")

                await self.pastikan_filter_submitted(tab_list)

                try:
                    semua_link = await self.ambil_semua_link(tab_list)
                except PlaywrightTimeout:
                    self.log("⚠️ Tabel tidak ditemukan. Berhenti.", "warn")
                    break

                link_baru = [l for l in semua_link if l["url"] not in sudah_diproses]

                if not link_baru:
                    self.log("✅ Semua ID sudah diproses! Klik refresh tabel...", "ok")
                    try:
                        tombol_refresh = await tab_list.wait_for_selector(
                            'button[ngbtooltip="Refresh Table"]', timeout=5_000
                        )
                        await tombol_refresh.click()
                        await self.jeda(2, 4)
                        await tab_list.wait_for_selector(
                            'td a[href*="assignment-detail"]',
                            timeout=self.config["timeout_tabel"]
                        )
                        await self.jeda()
                        semua_link_baru = await self.ambil_semua_link(tab_list)
                        link_baru_setelah_refresh = [
                            l for l in semua_link_baru
                            if l["url"] not in sudah_diproses
                        ]
                        if not link_baru_setelah_refresh:
                            self.log("✅ Tidak ada ID baru setelah refresh. Selesai!", "ok")
                            break
                        self.log(f"Ada {len(link_baru_setelah_refresh)} ID baru. Lanjut...")
                        continue
                    except PlaywrightTimeout:
                        self.log("⚠️ Tombol refresh tidak ditemukan. Berhenti.", "warn")
                        break

                for l in link_baru:
                    sudah_diproses.add(l["url"])

                total_link  = len(link_baru)
                batch_size  = self.config["batch_size"]
                total_batch = (total_link + batch_size - 1) // batch_size

                # Set progress total di awal putaran, reset current ke 0
                self._progress_current = 0
                self._progress_total   = total_link
                self.signals.progress.emit(0, total_link)
                self.log(f"Ditemukan {total_link} ID, diproses per batch {batch_size}...")

                for i in range(0, total_link, batch_size):
                    if self._stop:
                        break
                    batch     = link_baru[i:i + batch_size]
                    idx_batch = i // batch_size + 1
                    self.log(f"\nBatch {idx_batch}: {[b['teks'] for b in batch]}")
                    await self.proses_batch(context, batch, idx_batch, total_batch)
                    await self.jeda(2, 4)

            self.log(f"\n{'='*50}")
            self.log(
                f"SELESAI!  ✅ {self.counter_approve} approve  "
                f"⏭ {self.counter_skip} skip  ❌ {self.counter_error} error",
                "ok"
            )
            self.log(f"{'='*50}")
            await browser.close()

        self.signals.finished.emit()


# ─── THREAD RUNNER ────────────────────────────────────────────────────────────

class RunnerThread(QThread):
    def __init__(self, worker: FasihWorker):
        super().__init__()
        self.worker = worker

    def run(self):
        asyncio.run(self.worker.run())


# ─── MAIN WINDOW ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Approve FASIH GC PBI Tahap II (v2.0.0)")
        self.setMinimumSize(900, 650)
        self.is_dark = True
        self.runner  = None
        self.worker  = None
        self._build_ui()
        self._apply_theme()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        # ── Header ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title  = QLabel("🗳 Auto Approve FASIH GC PBI Tahap II")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        self.btn_theme = QToolButton()
        self.btn_theme.setText("☀️")
        self.btn_theme.setToolTip("Toggle Light/Dark Mode")
        self.btn_theme.clicked.connect(self._toggle_theme)
        header.addWidget(self.btn_theme)
        root.addLayout(header)

        # ── Separator ─────────────────────────────────────────────────────────
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        root.addWidget(sep)

        # ── Splitter: kiri config | kanan log ─────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, stretch=1)

        # ── Panel kiri ────────────────────────────────────────────────────────
        left = QWidget()
        left.setMaximumWidth(340)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(10)

        # Kredensial
        grp_login = QGroupBox("🔐 Kredensial")
        gl = QGridLayout(grp_login)
        gl.setColumnStretch(1, 1)
        gl.addWidget(QLabel("Username:"), 0, 0)
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("username SSO BPS")
        gl.addWidget(self.inp_user, 0, 1)

        gl.addWidget(QLabel("Password:"), 1, 0)
        self.inp_pass = QLineEdit()
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setPlaceholderText("••••••••")
        gl.addWidget(self.inp_pass, 1, 1)

        self.chk_show_pass = QCheckBox("Tampilkan password")
        self.chk_show_pass.toggled.connect(
            lambda c: self.inp_pass.setEchoMode(
                QLineEdit.EchoMode.Normal if c else QLineEdit.EchoMode.Password
            )
        )
        gl.addWidget(self.chk_show_pass, 2, 0, 1, 2)
        left_layout.addWidget(grp_login)

        # Pengaturan
        grp_cfg = QGroupBox("⚙️ Pengaturan")
        gc = QGridLayout(grp_cfg)
        gc.setColumnStretch(1, 1)

        lbl_batch = QLabel("Batch size:")
        gc.addWidget(lbl_batch, 0, 0)

        batch_row = QHBoxLayout()
        self.spin_batch = QSpinBox()
        self.spin_batch.setRange(1, 20)
        self.spin_batch.setValue(5)
        batch_row.addWidget(self.spin_batch)

        btn_info = QPushButton("?")
        btn_info.setFixedSize(20, 20)
        btn_info.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_info.setStyleSheet(
            "QPushButton {"
            "  border-radius: 10px;"
            "  border: 1px solid #6c7086;"
            "  font-weight: bold;"
            "  font-size: 11px;"
            "  padding: 0px;"
            "}"
            "QPushButton:hover { border-color: #89b4fa; color: #89b4fa; }"
        )
        btn_info.clicked.connect(lambda: QMessageBox.information(
            self, "Info Batch Size",
            "Jumlah tab ID yang dibuka sekaligus dalam satu batch.\n\n"
            "Nilai lebih besar → lebih cepat, tapi lebih berat di memori.\n"
            "Nilai lebih kecil → lebih aman, cocok untuk koneksi lambat.\n\n"
            "Disarankan: 3–5 untuk koneksi stabil."
        ))
        batch_row.addWidget(btn_info)
        batch_row.addStretch()

        gc.addLayout(batch_row, 0, 1)

        headless_row = QHBoxLayout()
        self.chk_headless = QCheckBox("Mode headless (browser invisible)")
        headless_row.addWidget(self.chk_headless)

        btn_info_headless = QPushButton("?")
        btn_info_headless.setFixedSize(20, 20)
        btn_info_headless.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_info_headless.setStyleSheet(
            "QPushButton {"
            "  border-radius: 10px;"
            "  border: 1px solid #6c7086;"
            "  font-weight: bold;"
            "  font-size: 11px;"
            "  padding: 0px;"
            "}"
            "QPushButton:hover { border-color: #89b4fa; color: #89b4fa; }"
        )
        btn_info_headless.clicked.connect(lambda: QMessageBox.information(
            self, "Info Mode Headless",
            "Jika diaktifkan, browser tidak akan ditampilkan di layar.\n\n"
            "Aktif → proses berjalan di background, lebih ringan.\n"
            "Nonaktif → browser terlihat, cocok untuk memantau proses.\n\n"
            "Disarankan: nonaktif dulu saat pertama kali mencoba. Jangan menutup browser yang muncul saat proses berjalan."
        ))
        headless_row.addWidget(btn_info_headless)
        headless_row.addStretch()
        gc.addLayout(headless_row, 1, 0, 1, 2)
        left_layout.addWidget(grp_cfg)

        # Tombol aksi
        btn_row = QHBoxLayout()
        self.btn_mulai = QPushButton("▶  Mulai")
        self.btn_mulai.setObjectName("btnMulai")
        self.btn_mulai.setMinimumHeight(40)
        self.btn_mulai.clicked.connect(self._mulai)

        self.btn_stop = QPushButton("■  Stop")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop)

        btn_row.addWidget(self.btn_mulai)
        btn_row.addWidget(self.btn_stop)
        left_layout.addLayout(btn_row)

        # Tombol bersihkan log
        self.btn_clear = QPushButton("🗑  Bersihkan Log")
        self.btn_clear.clicked.connect(lambda: self.log_area.clear())
        left_layout.addWidget(self.btn_clear)

        left_layout.addStretch()
        splitter.addWidget(left)

        # ── Panel kanan ───────────────────────────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        # Statistik
        grp_stat = QGroupBox("📊 Statistik")
        stat_row = QHBoxLayout(grp_stat)

        def _stat_col(emoji, label, color_attr):
            col = QVBoxLayout()
            lbl_val = QLabel("0")
            lbl_val.setObjectName("labelStat")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_val.setProperty("color_attr", color_attr)
            lbl_txt = QLabel(f"{emoji} {label}")
            lbl_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(lbl_val)
            col.addWidget(lbl_txt)
            return col, lbl_val

        col_ok,  self.lbl_approve = _stat_col("✅", "ID yang di-approve", "approve")
        col_skip, self.lbl_skip   = _stat_col("⏭",  "ID yang dilewati (sudah ter-approve/error)",    "skip")

        stat_row.addLayout(col_ok)
        stat_row.addLayout(col_skip)
        right_layout.addWidget(grp_stat)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("Menunggu...")
        right_layout.addWidget(self.progress)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(300)
        right_layout.addWidget(self.log_area, stretch=1)

        splitter.addWidget(right)
        splitter.setSizes([300, 600])

        # ── Status bar ────────────────────────────────────────────────────────
        self.statusBar().showMessage("Siap. Isi kredensial dan klik Mulai.")

    # ── Tema ──────────────────────────────────────────────────────────────────
    def _apply_theme(self):
        qss = DARK_QSS if self.is_dark else LIGHT_QSS
        self.setStyleSheet(qss)
        self.btn_theme.setText("☀️" if self.is_dark else "🌙")

        # Warna label statistik
        approve_color = "#a6e3a1" if self.is_dark else "#40a02b"
        skip_color    = "#f9e2af" if self.is_dark else "#df8e1d"

        self.lbl_approve.setStyleSheet(f"color: {approve_color};")
        self.lbl_skip.setStyleSheet(f"color: {skip_color};")

    def _toggle_theme(self):
        self.is_dark = not self.is_dark
        self._apply_theme()

    # ── Log helper ────────────────────────────────────────────────────────────
    def _append_log(self, msg: str, tipe: str):
        color_map = {
            "ok":   ("#a6e3a1", "#40a02b"),   # dark, light
            "warn": ("#f9e2af", "#df8e1d"),
            "err":  ("#f38ba8", "#d20f39"),
            "info": ("#cdd6f4", "#4c4f69"),
        }
        dark_c, light_c = color_map.get(tipe, color_map["info"])
        color = dark_c if self.is_dark else light_c

        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)
        self.log_area.insertHtml(
            f'<span style="color:{color};">{msg.replace("<","&lt;").replace(">","&gt;")}</span><br>'
        )
        self.log_area.ensureCursorVisible()

    # ── Mulai ─────────────────────────────────────────────────────────────────
    def _mulai(self):
        username = self.inp_user.text().strip()
        password = self.inp_pass.text()

        if not username or not password:
            QMessageBox.warning(self, "Perhatian", "Username dan password wajib diisi!")
            return

        config = {
            "username":       username,
            "password":       password,
            "batch_size":     self.spin_batch.value(),
            "jeda_min":       1.5,
            "jeda_max":       3.0,
            "timeout_review": 10000,
            "timeout_h1":     60000,
            "timeout_popup":  30000,
            "timeout_tabel":  15000,
            "headless":       self.chk_headless.isChecked(),
        }

        signals = WorkerSignals()
        signals.log_message.connect(self._append_log)
        signals.stat_update.connect(self._update_stat)
        signals.progress.connect(self._update_progress)
        signals.status_bar.connect(self.statusBar().showMessage)
        signals.started.connect(self._on_started)
        signals.finished.connect(self._on_finished)

        self.worker = FasihWorker(config, signals)
        self.runner = RunnerThread(self.worker)
        self.runner.start()

    # ── Stop ──────────────────────────────────────────────────────────────────
    def _stop(self):
        if self.worker:
            self.worker.stop()
            self.btn_stop.setEnabled(False)
            self.btn_stop.setText("⏳ Menghentikan...")
            self.statusBar().showMessage("Menghentikan... tunggu proses saat ini selesai.")

    # ── Callbacks ─────────────────────────────────────────────────────────────
    def _on_started(self):
        self.btn_mulai.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress.setFormat("Berjalan...")
        self.lbl_approve.setText("0")
        self.lbl_skip.setText("0")

    def _on_finished(self):
        self.btn_mulai.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setText("■  Stop")
        self.progress.setFormat("Selesai")
        self.statusBar().showMessage("Proses selesai.")

    def _update_stat(self, approve, skip):
        self.lbl_approve.setText(str(approve))
        self.lbl_skip.setText(str(skip))

    def _update_progress(self, current, total):
        if total == 0:
            return
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.progress.setFormat(f"{current}/{total} ID")

    # ── Closevent ─────────────────────────────────────────────────────────────
    def closeEvent(self, event):
        if self.runner and self.runner.isRunning():
            reply = QMessageBox.question(
                self, "Keluar",
                "Proses masih berjalan. Yakin ingin keluar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            if self.worker:
                self.worker.stop()
        event.accept()


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())