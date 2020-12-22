$(document).ready(function(){
    var list = document.getElementsByClassName('list-group')
    jQuery.each(device_json, function(key, value) { //create button for all devices
        var element = document.createElement('button') 
        element.onclick = function () {switch_active_element(this)}
        element.className = 'list-group-item list-group-item-action'
        
        element.innerHTML = value['PAD'] + ': ' + key;
        list[0].appendChild(element)
    })
    var status_byte = Number(request_json['ibsta']).toString(2)
    while (status_byte.length < 16){
        status_byte = "0" + status_byte
    }
    var i = 0
    var table_rows = document.getElementsByTagName('tbody')[0].children //header row not included
    for (var row of table_rows){
        if (status_byte[i] == 1){row.hidden = false}
        else{row.hidden = true}
        i = i + 1
    }
});


function start_loading_animation(element)
{
        element.innerHTML = "<i class='fa fa-spinner fa-spin'></i> loading..." 
}

function switch_active_element(element)
{
    var active_element = document.getElementsByName('active_element')[0]
    if (element.className == 'list-group-item list-group-item-action active') 
    { 
        element.className = 'list-group-item list-group-item-action'
        active_element.value = '' //reset active_element 
    }
    else 
    {
        var active_list_items = element.parentElement.getElementsByClassName('active')
        if (active_list_items.length != 0)
        {
            for (var item of active_list_items)
            {
                item.className = 'list-group-item list-group-item-action'
            }
        }
        element.className = 'list-group-item list-group-item-action active' 
        active_element.value = element.innerHTML.split(': ')[1]
    }
}

function refresh_dropdown(element) 
{
    var dropdown_label = element.parentElement.parentElement.getElementsByTagName('input')[0]
    dropdown_label.value = element.innerHTML
}

function change_coding(element)
{
    var ibsta = element.parentElement.parentElement.parentElement.getElementsByClassName('form-control')[0]
    var coding = element.innerHTML
    if (coding == 'binary')
    {
        var binary_value = Number(request_json['ibsta']).toString(2)
        while (binary_value.length < 16){
            binary_value = "0" + binary_value
        }
        ibsta.value = binary_value
    }
    else if (coding == 'decimal')
    {
        ibsta.value = Number(request_json['ibsta'])
    }
    else if (coding == 'hexadecimal')
    {
        ibsta.value = Number(request_json['ibsta']).toString(16)
    }
    
}

function validate_form()
{
    var no_error = true
    var error_message = ''
    var bytes_to_read = document.getElementsByName('bytes_to_read')[0]
    if ((bytes_to_read.value == '')||(isNumber(bytes_to_read.value) != true))
    {
        console.log('error')
        error_message = error_message + "\n bytes to read is empty or not an integer"
        bytes_to_read.className = 'form-control is-invalid'
        no_error = false
    }
    var active_element = document.getElementsByName('active_element')[0]
    if ((active_element.value == '')||(active_element.value in device_json != true))
    {
        error_message = error_message + "\n no valid device"
        active_element.className = 'form-control is-invalid'
        no_error = false
    }
    if (!no_error){alert(error_message)} 
    
    return no_error
}

function isNumber(number)
{
    return !isNaN(parseFloat(number)) && isFinite(number)
}
