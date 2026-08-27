/**
 * EthioBiz Desk Filters — P4-C Collapsible Filter Panel
 * Wraps every .filter-selector section in a collapsible container
 * with toggle behaviour persisted to localStorage.
 */
(function(){
  var LS_KEY="ebFiltersExpanded";
  function init(){
    if(!frappe.get_route||!frappe.get_route()[0]||frappe.get_route()[0]!=="List")return;
    var s=document.querySelector(".list-view .filter-selector, .frappe-list .filter-selector");
    if(!s||s.dataset.ebInit)return;
    s.dataset.ebInit="1";
    var lbl=s.querySelector(".filter-label, .list-filters .filter-button, h6");
    if(!lbl)return;
    var body=s.querySelector(".filter-body, .filter-menu");
    if(!body)return;
    lbl.innerHTML="<span class='collapse-indicator'>▼</span> "+lbl.innerHTML;
    var wrap=document.createElement("div");
    wrap.className="filter-section";
    lbl.parentNode.insertBefore(wrap,lbl);
    wrap.appendChild(lbl);wrap.appendChild(body);
    var saved=localStorage.getItem(LS_KEY);
    if(saved!==null)wrap.classList.toggle("collapsed",saved==="0");
    lbl.addEventListener("click",function(){
      wrap.classList.toggle("collapsed");
      localStorage.setItem(LS_KEY,wrap.classList.contains("collapsed")?"0":"1");
    });
  }
  frappe.realtime.on("list_view_refresh",function(){ setTimeout(init,600); });
  $(document).on("page-change",function(){ setTimeout(init,600); });
  $(function(){ setTimeout(init,800); });
})();
