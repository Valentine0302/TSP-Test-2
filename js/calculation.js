// Функция для перехода на страницу расчета
function navigateToCalculation(type) {
    switch(type) {
        case 'multimodal':
            window.location.href = 'calculation/multimodal.html';
            break;
        case 'europe':
            window.location.href = 'calculation/europe.html';
            break;
        case 'asia':
            window.location.href = 'calculation/asia.html';
            break;
        case 'sea_freight':
            window.location.href = 'calculation/sea_freight.html';
            break;
        default:
            alert('Страница расчета для данного типа перевозок находится в разработке');
    }
}
