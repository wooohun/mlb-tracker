

export function dateReformat(date) {
    const options = {
        weekday: 'narrow',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }

    var nDate = new Date(date).toLocaleDateString('en-US', options)
    nDate = nDate.substring(nDate.indexOf(' '))

    return nDate
}

export function convertHeight(ht) {

    var ft = Math.floor(ht / 12);
    var inch = ht % 12;

    var cm = ht * 2.54;

    const res = {
        imperial: ft + '\'' + inch + '\"',
        metric: cm,
    }
    return res
}

export function convertWeight(wt) {

}

export function getAge(dstr) {
    var today = new Date()
    var bday = new Date(dstr)

    var age = today.getFullYear() - bday.getFullYear()
    var m = today.getMonth() - bday.getMonth()

    if (m < 0 || (m === 0 && today.getDate() < bday.getDate())){
        age--;
    }
    return age
}