SELECT  `api_perkuliahan.nim`, 
        `api_mahasiswa.nama`, 
        `apiapi_mahasiswa.alamat`, 
        `api_mahasiswa.tanggal_lahir`,
        `api_matakuliah.kode_mk`,
        `api_matakuliah.nama_mk`,
        `api_matakuliah.sks`,
        `api_perkuliahan.nilai` FROM api_perkuliahan JOIN api_mahasiswa ON api_mahasiswa.nim=api_perkuliahan.nim JOIN api_matakuliah ON api_matakuliah.kode_mk=api_perkuliahan.kode_mk;