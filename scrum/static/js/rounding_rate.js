const authorRate = '.rateAuthor'
let rates = document.querySelectorAll('.rateAuthor')
// console.log(rates)

function newAuthorRate(rates) {
    rates.forEach(function (rate){
        rate.innerHTML = truncated(getFloat(rate.innerHTML))
        // console.log(rate.innerHTML)
    })
}

function truncated(num) {
    return Math.trunc(num * 10) / 10
}

function getFloat(num){
  return parseFloat(num.replace(/,/, '.'));
}

newAuthorRate(rates)

