$(function(){
    var JobList = function(container_elem, template_container_id) {
        this.elem = $(container_elem)
        this.searchConditions = {}
        this.searchUrl = window.bibos_job_search_url || './search/'
        this.statusSelectors = []
        BibOS.addTemplate('job-entry', template_container_id);
    }
    $.extend(JobList.prototype, {
        init: function() {
            var jobsearch = this
            $('#jobsearch-status-selectors input:checkbox').change(function() {
                jobsearch.search();
            })
            jobsearch.search();
        },

        appendEntries: function(dataList) {
            var container = this.elem
            $.each(dataList, function() {
                var item = $(BibOS.expandTemplate('job-entry', this))
                // Remove restart link unless job has failed
                if(this['label'] != 'label-important') {
                    var button = item.find('button.btn').first()
                    var content = button.attr('data-content')
                    content = content.substr(content.indexOf('<pre>'))
                    button.attr('data-content', content)
                }
                item.find('.btn').popover()
                item.find('input:checkbox').click(function() {
                    $(this).parents('tr').toggleClass('marked');
                });
                item.appendTo(container)
            })
        },

        replaceEntries: function(dataList) {
            this.elem.find('tr.muted').remove()
            this.appendEntries(dataList)
        },

        selectFilter: function(field, elem, val) {
            var e = $(elem)
            if(e.hasClass('selected')) {
                e.removeClass('selected');
                val = ''
            } else {
                e.parent().find('li').removeClass('selected');
                e.addClass('selected');
            }
            $('#jobsearch-filterform input[name=' + field + ']').val(val)
            this.search()
        },

        selectBatch: function(elem, val) {
            this.selectFilter('batch', elem, val)
        },

        selectPC: function(elem, val) {
            this.selectFilter('pc', elem, val)
        },

        selectGroup: function(elem, val) {
            this.selectFilter('group', elem, val)
        },

        orderby: function(order) {
            $('.orderby').each(function() {
              if ($(this).hasClass('order-' + order)) {
                $(this).addClass('active').find('i').toggleClass('icon-chevron-down icon-chevron-up').addClass('icon-white');
              } else {
                $(this).removeClass('active').find('i').attr('class', 'icon-chevron-down');
              };
            });
            
            var input = $('#jobsearch-filterform input[name=orderby]');
            input.val(BibOS.getOrderBy(input.val(), order))
            this.search()
        },

        search: function() {
            var js = this;
            js.searchConditions = $('#jobsearch-filterform').serialize()
            $.ajax({
                type: "POST",
                url: js.searchUrl,
                data: js.searchConditions,
                success: function(data) {
                    js.replaceEntries(data)
                },
                dataType: "json"
            });
        }
    });
    BibOS.JobList = new JobList('#job-list', '#jobitem-template');
    $(function() { BibOS.JobList.init() })
})