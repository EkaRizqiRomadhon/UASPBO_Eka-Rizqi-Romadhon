import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
from pathlib import Path
from abc import ABC, abstractmethod


# =========================
# ENCAPSULATION & INHERITANCE
# =========================

class BaseTransaction(ABC):
    """Base class abstrak untuk semua jenis transaksi (Encapsulation & Inheritance)"""
    
    def __init__(self, kategori, jumlah, keterangan, tanggal=None):
        # Private attributes (Encapsulation dengan name mangling)
        self.__kategori = kategori
        self.__jumlah = jumlah
        self.__keterangan = keterangan
        self.__tanggal = tanggal if tanggal else datetime.now().strftime("%Y-%m-%d %H:%M")
        self._tipe = None  # Protected attribute
    
    # Getter methods (Encapsulation)
    @property
    def kategori(self):
        return self.__kategori
    
    @property
    def jumlah(self):
        return self.__jumlah
    
    @property
    def keterangan(self):
        return self.__keterangan
    
    @property
    def tanggal(self):
        return self.__tanggal
    
    @property
    def tipe(self):
        return self._tipe
    
    # Setter methods (Encapsulation dengan validasi)
    @jumlah.setter
    def jumlah(self, value):
        if value <= 0:
            raise ValueError("Jumlah harus lebih dari 0")
        self.__jumlah = value
    
    @keterangan.setter
    def keterangan(self, value):
        self.__keterangan = value if value else "-"
    
    # Abstract method (akan di-override di child class - Polymorphism)
    @abstractmethod
    def get_icon(self):
        """Mengembalikan icon untuk tipe transaksi"""
        pass
    
    @abstractmethod
    def get_display_name(self):
        """Mengembalikan nama tampilan untuk tipe transaksi"""
        pass
    
    # Method untuk mengkalkulasi dampak transaksi (akan di-override - Polymorphism)
    @abstractmethod
    def calculate_impact(self):
        """Mengembalikan dampak transaksi terhadap saldo (+ atau -)"""
        pass
    
    def to_dict(self):
        """Konversi ke dictionary untuk penyimpanan"""
        return {
            'kategori': self.__kategori,
            'jumlah': self.__jumlah,
            'keterangan': self.__keterangan,
            'tipe': self._tipe,
            'tanggal': self.__tanggal
        }
    
    def format_currency(self):
        """Format jumlah ke format mata uang"""
        return f"Rp {self.__jumlah:,.0f}"


class Pengeluaran(BaseTransaction):
    """Class untuk transaksi pengeluaran (Inheritance dari BaseTransaction)"""
    
    def __init__(self, kategori, jumlah, keterangan, tanggal=None):
        super().__init__(kategori, jumlah, keterangan, tanggal)
        self._tipe = 'pengeluaran'
    
    # Polymorphism - Override method dari parent class
    def get_icon(self):
        return '💸'
    
    def get_display_name(self):
        return f"{self.get_icon()} Pengeluaran"
    
    def calculate_impact(self):
        """Pengeluaran mengurangi saldo"""
        return -self.jumlah
    
    def is_over_budget(self, budget_limit):
        """Method khusus untuk pengeluaran - mengecek apakah melebihi budget"""
        return self.jumlah > budget_limit


class Pemasukan(BaseTransaction):
    """Class untuk transaksi pemasukan (Inheritance dari BaseTransaction)"""
    
    def __init__(self, kategori, jumlah, keterangan, tanggal=None):
        super().__init__(kategori, jumlah, keterangan, tanggal)
        self._tipe = 'pemasukan'
    
    # Polymorphism - Override method dari parent class dengan behavior berbeda
    def get_icon(self):
        return '💰'
    
    def get_display_name(self):
        return f"{self.get_icon()} Pemasukan"
    
    def calculate_impact(self):
        """Pemasukan menambah saldo"""
        return self.jumlah
    
    def calculate_tax(self, tax_rate=0.05):
        """Method khusus untuk pemasukan - menghitung pajak"""
        return self.jumlah * tax_rate


# =========================
# FACTORY PATTERN
# =========================

class TransactionFactory:
    """Factory class untuk membuat objek transaksi (Encapsulation & Design Pattern)"""
    
    @staticmethod
    def create_transaction(tipe, kategori, jumlah, keterangan, tanggal=None):
        """Factory method untuk membuat transaksi berdasarkan tipe"""
        if tipe == 'pengeluaran':
            return Pengeluaran(kategori, jumlah, keterangan, tanggal)
        elif tipe == 'pemasukan':
            return Pemasukan(kategori, jumlah, keterangan, tanggal)
        else:
            raise ValueError(f"Tipe transaksi tidak valid: {tipe}")
    
    @staticmethod
    def from_dict(data):
        """Factory method untuk membuat transaksi dari dictionary"""
        return TransactionFactory.create_transaction(
            data['tipe'],
            data['kategori'],
            data['jumlah'],
            data['keterangan'],
            data['tanggal']
        )


# =========================
# DATA MANAGER (ENCAPSULATION)
# =========================

class DataManager:
    """Class untuk mengelola penyimpanan data (Encapsulation)"""
    
    def __init__(self, filename='money_tracker_data.json'):
        self.__filename = filename  # Private attribute
    
    def simpan_data(self, transaksi_list):
        """Menyimpan data ke file JSON"""
        data = [t.to_dict() for t in transaksi_list]
        try:
            with open(self.__filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error menyimpan data: {e}")
            return False
    
    def muat_data(self):
        """Memuat data dari file JSON"""
        try:
            if Path(self.__filename).exists():
                with open(self.__filename, 'r') as f:
                    data = json.load(f)
                return [TransactionFactory.from_dict(t) for t in data]
        except Exception as e:
            print(f"Error memuat data: {e}")
        return []


# =========================
# CALCULATOR (ENCAPSULATION)
# =========================

class FinancialCalculator:
    """Class untuk melakukan kalkulasi keuangan (Encapsulation & Single Responsibility)"""
    
    def __init__(self, transaksi_list):
        self.__transaksi_list = transaksi_list
    
    def hitung_total_pemasukan(self):
        """Menghitung total pemasukan menggunakan polymorphism"""
        return sum(
            t.calculate_impact() 
            for t in self.__transaksi_list 
            if isinstance(t, Pemasukan)
        )
    
    def hitung_total_pengeluaran(self):
        """Menghitung total pengeluaran (nilai absolut)"""
        return abs(sum(
            t.calculate_impact() 
            for t in self.__transaksi_list 
            if isinstance(t, Pengeluaran)
        ))
    
    def hitung_saldo(self):
        """Menghitung saldo menggunakan polymorphism"""
        # Demonstrasi polymorphism: setiap transaksi punya calculate_impact() berbeda
        return sum(t.calculate_impact() for t in self.__transaksi_list)
    
    def get_statistik(self):
        """Mendapatkan statistik lengkap"""
        return {
            'pemasukan': self.hitung_total_pemasukan(),
            'pengeluaran': self.hitung_total_pengeluaran(),
            'saldo': self.hitung_saldo()
        }


# =========================
# UI MANAGER (ENCAPSULATION)
# =========================

class UIManager:
    """Class untuk mengelola komponen UI (Encapsulation & Separation of Concerns)"""
    
    # Class variables (Encapsulation di level class)
    __KATEGORI_PENGELUARAN = [
        "🍔 Makanan & Minuman",
        "🚗 Transportasi",
        "🎮 Entertainment",
        "📱 Pulsa & Internet",
        "👕 Fashion & Shopping",
        "💊 Kesehatan",
        "📚 Pendidikan",
        "🏠 Kos/Sewa",
        "💳 Lainnya"
    ]
    
    __KATEGORI_PEMASUKAN = [
        "💰 Gaji/Uang Jajan",
        "💼 Freelance",
        "🛍️ Jualan Online",
        "🎁 Hadiah/Bonus",
        "💵 Lainnya"
    ]
    
    @classmethod
    def get_kategori_pengeluaran(cls):
        """Getter untuk kategori pengeluaran (Encapsulation)"""
        return cls.__KATEGORI_PENGELUARAN.copy()
    
    @classmethod
    def get_kategori_pemasukan(cls):
        """Getter untuk kategori pemasukan (Encapsulation)"""
        return cls.__KATEGORI_PEMASUKAN.copy()
    
    @staticmethod
    def create_summary_card(parent, title, color):
        """Factory method untuk membuat summary card"""
        card = tk.Frame(parent, bg=color, width=150, height=80)
        card.pack_propagate(False)
        
        tk.Label(
            card,
            text=title,
            bg=color,
            fg='white',
            font=('Arial', 9, 'bold')
        ).pack(pady=(10, 5))
        
        label = tk.Label(
            card,
            text="Rp 0",
            bg=color,
            fg='white',
            font=('Arial', 14, 'bold')
        )
        label.pack()
        
        card.label = label
        return card


# =========================
# MAIN APPLICATION
# =========================

class MoneyTrackerApp:
    """Class utama aplikasi dengan OOP principles lengkap"""
    
    def __init__(self, root):
        self.__root = root  # Private attribute
        self.__root.title("💰 Pencatat Keuangan")
        self.__root.geometry("1200x600")
        self.__root.resizable(False, False)
        self.__root.configure(bg='#f0f0f0')
        
        # Composition: Menggunakan object dari class lain (Encapsulation)
        self.__data_manager = DataManager()
        self.__transaksi_list = self.__data_manager.muat_data()
        self.__calculator = FinancialCalculator(self.__transaksi_list)
        
        # Setup UI
        self.__setup_ui()
        self.__update_display()
    
    def __setup_ui(self):
        """Setup UI - Private method (Encapsulation)"""
        # Header
        header_frame = tk.Frame(self.__root, bg='#4CAF50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="💰 Manajemen Keuangan",
            font=('Arial', 24, 'bold'),
            bg='#4CAF50',
            fg='white'
        ).pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.__root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left & Right panels
        self.__setup_input_panel(main_container)
        self.__setup_display_panel(main_container)
    
    def __setup_input_panel(self, parent):
        """Setup panel input - Private method"""
        input_frame = tk.LabelFrame(
            parent,
            text="📝 Tambah Transaksi",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=15,
            pady=15
        )
        input_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Tipe transaksi
        tk.Label(input_frame, text="Tipe:", bg='white', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.__tipe_var = tk.StringVar(value='pengeluaran')
        
        tipe_frame = tk.Frame(input_frame, bg='white')
        tipe_frame.grid(row=0, column=1, sticky='w', pady=5)
        
        tk.Radiobutton(
            tipe_frame,
            text="💸 Pengeluaran",
            variable=self.__tipe_var,
            value='pengeluaran',
            bg='white',
            command=self.__update_kategori_list
        ).pack(side='left', padx=5)
        
        tk.Radiobutton(
            tipe_frame,
            text="💰 Pemasukan",
            variable=self.__tipe_var,
            value='pemasukan',
            bg='white',
            command=self.__update_kategori_list
        ).pack(side='left', padx=5)
        
        # Kategori
        tk.Label(input_frame, text="Kategori:", bg='white', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.__kategori_combo = ttk.Combobox(input_frame, width=25, state='readonly')
        self.__kategori_combo.grid(row=1, column=1, sticky='w', pady=5)
        self.__update_kategori_list()
        
        # Jumlah
        tk.Label(input_frame, text="Jumlah (Rp):", bg='white', font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        self.__jumlah_entry = tk.Entry(input_frame, width=27, font=('Arial', 10))
        self.__jumlah_entry.grid(row=2, column=1, sticky='w', pady=5)
        
        # Keterangan
        tk.Label(input_frame, text="Keterangan:", bg='white', font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=5)
        self.__keterangan_entry = tk.Entry(input_frame, width=27, font=('Arial', 10))
        self.__keterangan_entry.grid(row=3, column=1, sticky='w', pady=5)
        
        # Tombol
        btn_frame = tk.Frame(input_frame, bg='white')
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Button(
            btn_frame,
            text="✅ Tambah",
            command=self.__tambah_transaksi,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ Hapus Terpilih",
            command=self.__hapus_transaksi,
            bg='#f44336',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side='left', padx=5)
    
    def __setup_display_panel(self, parent):
        """Setup panel display - Private method"""
        display_frame = tk.Frame(parent, bg='#f0f0f0')
        display_frame.grid(row=0, column=1, sticky='nsew')
        
        # Summary cards menggunakan UIManager
        summary_frame = tk.Frame(display_frame, bg='#f0f0f0')
        summary_frame.pack(fill='x', pady=(0, 10))
        
        self.__pemasukan_frame = UIManager.create_summary_card(
            summary_frame, "💰 Total Pemasukan", "#4CAF50"
        )
        self.__pemasukan_frame.pack(side='left', padx=5)
        
        self.__pengeluaran_frame = UIManager.create_summary_card(
            summary_frame, "💸 Total Pengeluaran", "#f44336"
        )
        self.__pengeluaran_frame.pack(side='left', padx=5)
        
        self.__saldo_frame = UIManager.create_summary_card(
            summary_frame, "💳 Saldo", "#2196F3"
        )
        self.__saldo_frame.pack(side='left', padx=5)
        
        # List transaksi
        list_frame = tk.LabelFrame(
            display_frame,
            text="📜 Riwayat Transaksi",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=10,
            pady=10
        )
        list_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('Tanggal', 'Tipe', 'Kategori', 'Jumlah', 'Keterangan')
        self.__tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.__tree.heading('Tanggal', text='Tanggal')
        self.__tree.heading('Tipe', text='Tipe')
        self.__tree.heading('Kategori', text='Kategori')
        self.__tree.heading('Jumlah', text='Jumlah (Rp)')
        self.__tree.heading('Keterangan', text='Keterangan')
        
        self.__tree.column('Tanggal', width=120)
        self.__tree.column('Tipe', width=80)
        self.__tree.column('Kategori', width=150)
        self.__tree.column('Jumlah', width=100)
        self.__tree.column('Keterangan', width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.__tree.yview)
        self.__tree.configure(yscrollcommand=scrollbar.set)
        
        self.__tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=2)
        parent.rowconfigure(0, weight=1)
    
    def __update_kategori_list(self):
        """Update kategori list - Private method"""
        if self.__tipe_var.get() == 'pengeluaran':
            self.__kategori_combo['values'] = UIManager.get_kategori_pengeluaran()
        else:
            self.__kategori_combo['values'] = UIManager.get_kategori_pemasukan()
        
        if len(self.__kategori_combo['values']) > 0:
            self.__kategori_combo.current(0)
    
    def __tambah_transaksi(self):
        """Tambah transaksi - Private method, menggunakan Factory Pattern"""
        try:
            jumlah = float(self.__jumlah_entry.get())
            if jumlah <= 0:
                raise ValueError("Jumlah harus lebih dari 0")
            
            kategori = self.__kategori_combo.get()
            keterangan = self.__keterangan_entry.get() or "-"
            tipe = self.__tipe_var.get()
            
            # Menggunakan Factory untuk membuat transaksi (Polymorphism)
            transaksi = TransactionFactory.create_transaction(
                tipe, kategori, jumlah, keterangan
            )
            
            self.__transaksi_list.append(transaksi)
            
            # Update calculator dengan list baru
            self.__calculator = FinancialCalculator(self.__transaksi_list)
            
            # Simpan ke file
            self.__data_manager.simpan_data(self.__transaksi_list)
            
            # Clear inputs
            self.__jumlah_entry.delete(0, tk.END)
            self.__keterangan_entry.delete(0, tk.END)
            
            # Update display
            self.__update_display()
            
            messagebox.showinfo("Sukses", "Transaksi berhasil ditambahkan! 🎉")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Input tidak valid: {str(e)}")
    
    def __hapus_transaksi(self):
        """Hapus transaksi - Private method"""
        selected = self.__tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih transaksi yang ingin dihapus!")
            return
        
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus transaksi ini?"):
            # Karena treeview menampilkan reversed, kita perlu konversi index
            tree_index = self.__tree.index(selected[0])
            # Index sebenarnya di list (karena reversed)
            actual_index = len(self.__transaksi_list) - 1 - tree_index
            
            del self.__transaksi_list[actual_index]
            
            # Update calculator
            self.__calculator = FinancialCalculator(self.__transaksi_list)
            
            # Simpan ke file
            self.__data_manager.simpan_data(self.__transaksi_list)
            
            # Update display
            self.__update_display()
            messagebox.showinfo("Sukses", "Transaksi berhasil dihapus!")
    
    def __update_display(self):
        """Update display - Private method, demonstrasi Polymorphism"""
        # Menggunakan calculator untuk mendapatkan statistik
        stats = self.__calculator.get_statistik()
        
        # Update cards
        self.__pemasukan_frame.label.config(text=f"Rp {stats['pemasukan']:,.0f}")
        self.__pengeluaran_frame.label.config(text=f"Rp {stats['pengeluaran']:,.0f}")
        self.__saldo_frame.label.config(text=f"Rp {stats['saldo']:,.0f}")
        
        # Update treeview - Demonstrasi Polymorphism
        for item in self.__tree.get_children():
            self.__tree.delete(item)
        
        for transaksi in reversed(self.__transaksi_list):
            # Polymorphism: get_display_name() berbeda untuk Pemasukan dan Pengeluaran
            self.__tree.insert('', 'end', values=(
                transaksi.tanggal,
                transaksi.get_display_name(),  # Method polymorphic
                transaksi.kategori,
                transaksi.format_currency(),
                transaksi.keterangan
            ))


def main():
    root = tk.Tk()
    app = MoneyTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()