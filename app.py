import streamlit as st
import pandas as pd

# ==========================================
# 1. MODUL CYK
# ==========================================

def cyk_parser(kalimat, grammar):
    words = kalimat.lower().split()
    n = len(words)
    # table[baris][kolom] -> menyimpan dictionary {Simbol: Data_Turunan}
    table = [[{} for _ in range(n - i)] for i in range(n)]

    # Langkah 1: Leksikal (Isi Baris Dasar)
    for i, word in enumerate(words):
        for lhs, rhs_list in grammar.items():
            for rhs in rhs_list:
                if len(rhs) == 1 and rhs[0] == word:
                    table[0][i][lhs] = word 

    # Langkah 2: Sintaksis (Gabungkan Frasa)
    for j in range(1, n): 
        for i in range(n - j):
            for k in range(j):
                left_cell = table[k][i]
                right_cell = table[j - k - 1][i + k + 1]
                
                for lhs, rhs_list in grammar.items():
                    for rhs in rhs_list:
                        if len(rhs) == 2:
                            if rhs[0] in left_cell and rhs[1] in right_cell:
                                # Simpan info untuk rekonstruksi pohon teks
                                table[j][i][lhs] = {
                                    "left": {"sym": rhs[0], "row": k, "col": i},
                                    "right": {"sym": rhs[1], "row": j - k - 1, "col": i + k + 1}
                                }
    return table, words

def get_text_tree(table, words, row, col, symbol, prefix=""):
    """
    Menghasilkan parse tree dalam bentuk teks murni (monospace),
    cocok untuk ditampilkan dengan st.code()
    """
    node_data = table[row][col].get(symbol)

    # Terminal (kata asli)
    if isinstance(node_data, str):
        return f"{prefix}└── {symbol} : {node_data}\n"

    # Non-terminal (punya cabang)
    left = node_data["left"]
    right = node_data["right"]

    result = f"{prefix}├── {symbol}\n"
    result += get_text_tree(
        table, words,
        left["row"], left["col"], left["sym"],
        prefix + "│   "
    )
    result += get_text_tree(
        table, words,
        right["row"], right["col"], right["sym"],
        prefix + "    "
    )
    return result

# ==========================================
# 2. DATASET & RULE CFG
# ==========================================

# Dataset 
nouns = "kamar udeng kelase natahe batare jalerne tunangan buku titine ujan semeng pekene sanja meja kelas rurunge setra denpasar peteng tongose paruman lumure kopi semengan umah pekak pondokan aplikasi pamalajahan aksara bali pot bungan pucuk kolam budidaya be koi gurune teteladanan margi kendaraan cuaca aktivitas entasin plalianan bahasa anak smp pitaken kasut jejaitan otonan luh putu desa penglu kwaca limane lutung objek wisata wewidangan lingsir sandal ajengan gegaenan sari sapu pabersihan sekolahane madingehan munyin suling i ketut garing bale sandat dadong salak gula pasir meme peken puskesmas corak batik pameliang bapa gianyar sastra kandang bucu margine mejane siswa".split()
adjectives = "cenik mael bersih tis belig lantang jegeg tebel dueg bales rame daki sepi nyeh linggah kiap cupit kedas luung ning becik ageng aluh cocok rimbit bedik iing jaen jangih miik manis pantes tegeh".split()
adverbs = "sajan bes gati paling kuang pisan ngangsan ngalub nenten tuni dibi semengan mangkin pedidi".split()
determiners = "ento tiang adi ene puniki punika i".split()
prepositions = "di ke rikala anggo anggon nuju antuk dibi ring tuni uli".split()

bali_grammar = {
    "K": [["P", "S"], ["P", "X1"], ["P", "X2"], ["P", "X3"], ["P", "X4"], ["P", "X5"]],
    "X1": [["S", "Ket"]],
    "X2": [["S", "Pel"]],
    "X3": [["Pel", "S"]],
    "X4": [["Pel", "X1"]],
    "X5": [["S", "X6"]],
    "X6": [["Pel", "Ket"]],
    "P": [["Adj", "Adv"], ["Adv", "Adj"]] + [[a] for a in adjectives],
    "S": [["NP", "Noun"], ["Noun", "Det"], ["Det", "Noun"], ["NP", "Det"], ["Noun", "Adj"], ["Noun", "Adv"]],
    "Pel": [["Det", "Noun"], ["Noun", "Adj"], ["Noun", "Adv"], ["Prep", "NP"]],
    "Ket": [["Prep", "NP"], ["Adv", "Noun"]],
    "NP": [["NP", "Noun"], ["Noun", "Det"], ["Det", "Noun"], ["NP", "Det"], ["Noun", "Adj"], ["Noun", "Adv"]],
    "Prep": [[p] for p in prepositions],
    "Noun": [[n] for n in nouns],
    "Adj": [[a] for a in adjectives],
    "Adv": [[av] for av in adverbs],
    "Det": [[d] for d in determiners]
}

# ==========================================
# 3. UI STREAMLIT
# ==========================================

st.set_page_config(page_title="BaliParser Lite", page_icon="📝")

st.title("Program Parsing Kalimat Bahasa Bali")
st.subheader("Pengecekan Kalimat Predikat Frasa Adjektiva")

input_kalimat = st.text_input("Masukkan Kalimat Bahasa Bali:", placeholder="Contoh: jaen sajan kopi puniki")

if input_kalimat:
    tabel, kata = cyk_parser(input_kalimat, bali_grammar)
    n = len(kata)
    
    # Simbol K harus ada di sel paling atas
    is_valid = "K" in tabel[n-1][0] if n > 0 else False
    
    if is_valid:
        st.success("Kalimat VALID")
        
        # Penjelasan 
        with st.container():
            st.write("Struktur Pohon (Parse Tree)")
            tree_text = get_text_tree(tabel, kata, n-1, 0, "K")
            st.code(tree_text, language="text")


        with st.expander("Lihat Detail Proses (Tabel CYK)"):
            # Membuat tampilan tabel matrix yang lebih cantik
            matrix_data = []
            for r in reversed(range(n)):
                row = []
                for c in range(len(tabel[r])):
                    val = ", ".join(tabel[r][c].keys()) if tabel[r][c] else "Ø"
                    row.append(val)
                # Padding untuk sel yang kosong agar rapi di dataframe
                while len(row) < n:
                    row.append("-")
                matrix_data.append(row)
            
            df = pd.DataFrame(matrix_data)
            st.table(df)
            
    else:
        st.error("Kalimat TIDAK VALID")
        st.info("Saran: Cek apakah kata sudah masuk dataset atau pastikan pola adalah Predikat di awal.")

# Sidebar Informasi
with st.sidebar:
    st.markdown("### Statistik Dataset")
    st.write(f"**Noun:** {len(nouns)} kata")
    st.write(f"**Adj:** {len(adjectives)} kata")
    st.write(f"**Adv:** {len(adverbs)} kata")
    st.write("---")
    st.write("Aplikasi ini menggunakan algoritma CYK untuk membedah struktur kalimat secara bertahap.")