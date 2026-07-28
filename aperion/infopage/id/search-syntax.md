# Sintaks Pencarian

Aperion Search dilengkapi dengan sintaks pencarian yang memungkinkan Anda mengubah kategori,
mesin pencari, bahasa, dan lainnya. Lihat {{link(‘preferences’, ‘preferences’)}} untuk
daftar mesin pencari, kategori, dan bahasa.

## `!` Pilih mesin pencari dan kategori

Untuk menetapkan nama kategori dan/atau mesin pencari, gunakan awalan `!`. Berikut beberapa contoh:

- Cari Wikipedia untuk **paris**:

  - {{search(‘!wp paris’)}}
  - {{search(‘!wikipedia paris’)}}

- Cari dalam kategori **map** untuk **paris**:

  - {{search(‘!map paris’)}}

- Pencarian gambar

  - {{search(‘!images Wau Holland’)}}

Singkatan mesin pencari dan bahasa juga diterima. Modifier mesin/kategori
dapat digabungkan dan inklusif. Misalnya, {{search('!map !ddg !wp
paris')}} mencari di kategori peta dan mencari DuckDuckGo dan Wikipedia untuk **paris**.

## `:` Pilih bahasa

Untuk memilih filter bahasa, gunakan awalan `:`.  Contoh:

- Cari Wikipedia dengan bahasa kustom:

  - {{search(‘:fr !wp Wau Holland’)}}

## `!!<bang>` Bang eksternal

Aperion Search mendukung bang eksternal dari [DuckDuckGo]. Untuk langsung melompat ke halaman
pencarian eksternal, gunakan awalan `!!`. Sebagai contoh:

- Cari Wikipedia dengan bahasa kustom:

  - {{search(‘!!wfr Wau Holland’)}}

Harap diperhatikan bahwa pencarian Anda akan dilakukan langsung di mesin pencari eksternal.  Aperion Search tidak dapat melindungi privasi Anda dengan ini.

[DuckDuckGo]: https://duckduckgo.com/bang

## `!!` pengalihan otomatis

Saat menyertakan `!!` dengan