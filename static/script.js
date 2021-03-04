const city_list = {
    'seoul': ['강남/역삼/삼성/신사/청담', '서초/교대', '잠실/송파/왕십리/강동', '을지로/시청/명동', '종로/인사동/동대문/강북', '서울역/이태원/용산', '마포/홍대/신촌/서대문', '영등포/여의도/김포공항', '구로/금천/관악/동작'],
    'busan': ['해운대/센텀/송정', '광안리/기장', '부산역/남포/자갈치/영도', '서면/동래/연제/남구', '김해공항/기타 (그외 지역)'],
    'jeju': ['제주공항/애월/함덕', '서귀포시/중문/표선/성산']
};

let state = document.getElementById('state-select');
let city = document.getElementById('city-select');

state.addEventListener('change', function () {
    let selected = city_list[this.value];

    while (city.options.length > 0) {
        city.options.remove(0);
    }

    Array.from(selected).forEach(function (x) {
        let option = new Option(x, x.split('/')[0]);
        city.appendChild(option);
    });
});