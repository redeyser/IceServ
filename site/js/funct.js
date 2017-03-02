function _putfile(page) {
    var file = document.getElementById("file");
    file=file.files[0]
    if (!file) { return; }
    var xhr = new XMLHttpRequest();
    xhr.open("POST", page, false);
    var formData = new FormData();
    formData.append("file", file);
    xhr.send(formData);
    return xhr.responseText;
}

function _getdata(page){
    var xhrp = new XMLHttpRequest();
    xhrp.open('GET', page, false);
    xhrp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhrp.send();
        if (xhrp.status != 200) {
            alert( xhrp.status + ': ' + xhrp.statusText );
            return '#err';
        } else {
            return xhrp.responseText;
        }
        return '#err';
}

function _postdata(page,a_params,a_values){
    var xhrp = new XMLHttpRequest();
    xhrp.open('POST', page, false);
    xhrp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    body="";
    for(var i=0; i<a_params.length; i++) {
        n=a_params[i];
        v=a_values[i];
        if (body.length>0){add="&";}else{add="";}
        body = body + add + n + "=" + encodeURIComponent(v);
    }
    xhrp.send(body);
        if (xhrp.status != 200) {
            alert( xhrp.status + ': ' + xhrp.statusText );
            return '#err';
        } else {
            return xhrp.responseText;
        }
        return '#err';
}

function _relocate(page){
    window.location=page;
}

function edit_x(n,id){
    ed_content=_getdata("/"+n+"?id="+id);
    ed_x.innerHTML="<div class='infoline center norm'> Edit "+n+"</div>"+ed_content;
    if (n=='action'){
        days=daysweek.value;
        s="";w=['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС'];
        for (i=1;i<=7;i++){
            on='setweekday(this);';
            if (days[i-1]=="0"){
                cl='black';
            }else{cl='tbs';}
            s+="<td id='day_"+(i-1)+"' onclick='"+on+"' class='"+cl+"'>"+w[i-1]+"</td>";
        }
        s="<table class='small warn tb'><tr>"+s+"</tr></table>";
        daysw.innerHTML=s;
    }
    ed_x.hidden=false;
}
function setweekday(t){
    if (t.className=='tbs'){
        t.className='black';
    }else{
        t.className='tbs';
    }
    days="";
    for (i=0;i<7;i++){
        t=document.getElementById('day_'+i);
        if (t.className=='tbs'){
            days+='1';
        }else{
            days+='0';
        }
    }
    daysweek.value=days;
}
  function edtext(n){
    _N=n;
    v=document.getElementById(n);
    t=document.getElementById("text");
    t.value=v.value;
  }
  function savetext(){
    v=document.getElementById(_N);
    t=document.getElementById("text");
    v.value=t.value;
  }
function edit_reg(idreg){
    ed_content=_getdata("/reg?idreg="+idreg);
    ed_reg.innerHTML="<div class='infoline center norm'> Edit Reg</div>"+ed_content;
    ed_reg.hidden=false;
}

function edit_sets(group){
    ed_content=_getdata("/sets_get?group="+group);
    ed_sets.innerHTML="<div class='infoline center norm'> Редактирование настроек</div>"+ed_content;
    ed_sets.hidden=false;
}

function edit_autosets(){
    ed_content=_getdata("/sets/autosets");
    ed_sets.innerHTML="<div class='infoline center norm'> Редактирование настроек</div>"+ed_content;
    ed_sets.hidden=false;
}

function ch_dev(v){
        ed_content=_getdata("/printer?idprinter="+v);
        if (ed_content!='0'){
            ed_drv.innerHTML="<div class='infoline center'> Подключение принтера </div>"+ed_content;
            ed_drv.hidden=false;
        }
}
function alert_message(head,content){
  message_content.innerHTML="<div class='infoline center'>"+head+"</div>"+content;
  message.hidden=false;
//  message_btn.focus();
}
function get_gplace_ct(){
    if (id.value=='0'){
        return;
    }
    ct=_getdata("/gplace_ct?id="+id.value);
    j=JSON.parse(ct);
    gplaces={};
    cont="";
    for (i in j){
        p=j[i];
        if (p[0]=='1'){
            cl='flame';
        }else { cl='black'; }
        tb="";
        for (n=1;n<=3;n++){
            tb+="<td>"+p[n]+"</td>";
        }
        tr="<tr id='tr_"+p[1]+"'class='"+cl+"' onclick='set_gplace(this);'>"+tb+"</tr>";
        cont+=tr;
        gplaces[p[1]]=p[0];
    }
    cont="<table class='tb small black'>"+cont+"</table>";
    cont+="<button class='but norm marg' onclick='ed_sub.hidden=true;'>Cancel</button>";
    cont+="<button class='but norm marg' name='save' value='save' onclick='save_gplaces();' >Save</button>";
    tb_content.innerHTML="<div class='infoline center norm'>include place</div>"+cont;
    ed_sub.hidden=false;
}
function set_gplace(t){
    _id=t.id.substr(3);
    if (t.className=='flame'){
        t.className='black';
        gplaces[_id]='0';
    }else{
        t.className='flame';
        gplaces[_id]='1';
    }
}
function save_gplaces(){
 jgplaces=JSON.stringify(gplaces);
 r=_postdata("/gplace_ct",['gplaces','id'],[jgplaces,id.value]);
 ed_sub.hidden=true;
}
function get_tlist(id){
    return _getdata("/tlist_ct?id="+id);
}
function get_price(parent){
    return _getdata("/get_price?parent="+parent+"&idprice="+idprice.value);
}
function init_sprice(){
    sprice={};
}
function sel_price(parent){
    t=get_tlist(id.value);
    sprice=JSON.parse(t);
    r=get_price(parent);
    if (r=="0"){
        return;
    }
    json=JSON.parse(r);
    c=0;
    popcursor=0;
    content="";
    for (var i in json){
        c=c+1;
        key=json[i];
        _code=key[2];
        if (c==1){popcursor=_code;}
        if (popcursor==_code){ cs="tbs";  }else{ cs=""; }
        _name=key[4];
        _istov=key[18];
        _cena=parseFloat(key[6]).toFixed(2);
        _ost=parseFloat(key[7]).toFixed(2);
        if (_istov==1){ ls="ice";  }else{  ls="flame";  }
        on="sel_price("+_code+");";
        ln="<tr ondblclick='"+on+"' onclick='setpopcursor("+_code+");' class='"+cs+"' id='poptr_"+_code+"'>"+
        "<td class='"+ls+"'>"+_code+"</td>"+
        "<td class='"+ls+"' id='poptd_"+_code+"'>"+_name+"</td><td onclick='add_sprice("+_code+");'>&gt&gt</td></tr>";
        content+=ln;
    }
    c="<div class='infoline small center'>Выбор номенклатуры</div>"+
    "<table style='margin-left:2%;width:95%;height:95%'><tr><td width=50%>"+
      "<div class='scroll' style='position:relative;height:95%'>"+
       "<table class='tbm smallest black' style='margin-left:2%;width:95%'><tbody>"+
        "<tr>"+
         "<td onclick='sel_price(0);'>\\</td>"+
         "<td class='but' onclick='save_sprice();'>Сохранить</td>"+
         "<td class='but' onclick='popprice.hidden=true;'>Отменить</td>"+
        "</tr>"+
        "<tr><th>Код</th><th>Номенклатура</th><th>Добавить</th></tr>"+
        content+
       "</tbody></table>"+
    "</div>"+
    "</td><td>"+
      "<div class='scroll' style='position:relative;height:95%'>"+
      "<table id='selected_price' class='tbm smallest black' style='margin-left:2%;width:95%'><tbody>"+
      "<tr><th>Код</th><th>Номенклатура</th><th>Удалить</th></tr>"+
      "</tbody</table></div>"+
    "</td></tr></table>";
    popprice.innerHTML=c;
    popprice.hidden=false;
    fill_sprice();
    //popup_btn.focus();
    //lenpoppos=c;
    //_result("Выбор номенклатуры");
}
function fill_sprice(){
    cnt="";
    for (i in sprice){
        cnt+="<tr>"+
        "<td onclick='del_sprice("+i+");'>&lt&lt</td>"+
        "<td class='bold'>"+i+"</td>"+
        "<td>"+sprice[i]+"</td>"+
        "</tr>";
    }
    selected_price.innerHTML=cnt;
}
function setpopcursor(cur){
        pos="poptr_"+popcursor;
        e=document.getElementById(pos);
        e.className="";
        popcursor=cur;
        pos="poptr_"+popcursor;
        e=document.getElementById(pos);
        e.className="tbs";

}
function save_sprice(){
    jsprice=JSON.stringify(sprice);
    r= _postdata("/tlist_ct",["id","sprice"],[id.value,jsprice]);
    popprice.hidden=true;
}
function add_sprice(cur){
        pos="poptd_"+cur;
        e=document.getElementById(pos);
        sprice[cur]=e.innerHTML;
        fill_sprice();
}
function del_sprice(cur){
        delete sprice[cur];
        fill_sprice();
}
