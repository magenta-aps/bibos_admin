// Set up global BibOS instance used for accessing utility methods
var BibOS;
(function($) {
  function BibOS(args) {
    this.templates = {};
    this.documentReady = false
    this.loadedItems = {}
    this.scriptsToLoad = []
    this.cssToLoad = []
    this.shownJobInfo = -1;
  }

  var documentaion_match = /^(https?:\/\/[^\/]+)?\/documentation\//;
  var back_match = /[\?\&]back=([^\&]+)/;

  $.extend(BibOS.prototype, {
    init: function() {
    },

    onDOMReady: function() {
      var t = this;
      t.documentReady = true;

      // Mark what we have already loaded
      $('script').each(function() {
        t.loadedItems[$(this).attr('src') || ''] = true
      })
      $.each(this.scriptsToLoad, function() {
        t.loadScript(this)
      })
      $('link').each(function() {
        t.loadedItems[$(this).attr('href') || ''] = true
      })
      $.each(this.cssToLoad, function() {
        t.loadStylesheet(this)
      })

      $('#editconfig_value').attr('maxlength', 4096)

      var m = document.cookie.match(/\bbibos-notification\s*=\s*([^;]+)/)
      if(m) {
        try {
          var descriptor = JSON.parse(decodeURIComponent(m[1]));
          notification = $('.bibos-notification').first()
          if (descriptor["type"] == "error")
            notification.addClass("errorlist")
          notification.html(descriptor["message"]).fadeIn()
        } catch (e) {
          /* If there was an exception here, then the cookie was malformed --
             print the exception to the console and continue, clearing the
             broken cookie */
          console.error(e)
        }
        document.cookie = 'bibos-notification=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/';
      }

      if(location.href.match(documentaion_match))
        this.setupDocumentationBackLinks();
      $('body').on('click', function(e) {
        return t.onBodyClick(e);
      })
    },
    setupDocumentationBackLinks: function() {
      var ref = document.referrer || '';
      var back = '';

      var m = ref.match(back_match) || location.href.match(back_match);
      if(m) {
        back = unescape(m[1]);
      } else if(!ref.match(documentaion_match)) {
        back = ref
      }

      if(! back)
        return

      back = escape(back);
      $('a').each(function() {
        var href = $(this).attr('href') || '';
        if(href == '#' || href.match(/^javascript:/))
          return true;
        if(href.match(documentaion_match)) {
          var url_parts = href.split(/[\?#]/);
          var qstring_parts = (url_parts[1] || '').split('&');
          var args = []
          $.each(qstring_parts, function() {
            if(this != '' && !this.match(/back=/))
              args.push(this)
          });
          args.push('back=' + back);
          var new_href = [
            url_parts[0],
            '?', args.join('&'),
          ].join('');
          if(url_parts.length > 2) {
            url_parts.splice(0, 2);
            new_href += '#' + url_parts.join("#");
          }
          $(this).attr('href', new_href);
        }
        return true;
      })
    },
    loadResource: function(type, src) {
      if(this.documentReady) {
        var item;
        if(this.loadedItems[src])
          return
        if(type == 'css' || type == 'stylesheet') {
          var css = $('<link>', {
            'href': src,
            'type': 'text/css',
            'rel': 'stylesheet'
          });
          css.appendTo($('head'));
        } else if(type == 'script' || type == 'javascript') {
          var script = $('<script>', {'src': src, 'type':'text/javascript'});
          script.appendTo($('body'));
        } else {
          alert("Don't know how to load item of type " + type);
          return
        }
        this.loadedItems[src] = true;
      } else {
        if (type == 'css' || type == 'stylesheet') {
          this.cssToLoad.push(src)
        } else if(type == 'script') {
          this.scriptsToLoad.push(src)
        } else {
          alert("Don't know how to load item of type " + type + ' once')
        }
      }
    },

    loadScript: function(src) {
      this.loadResource('script', src);
    },

    loadStylesheet: function(src) {
      this.loadResource('css', src);
    },

    translate: function() {
      // TODO: implement actual translation, this is just poor man's sprintf
      var args = arguments, arg_idx = 1, key = arguments[0] || '';
      if (arguments.length > 1) {
        key = key.replace(/\%s/g, function(m) {
          var v = args[arg_idx++];
          return v == undefined ? '' : v;
        })
      }
      return key
    },

    // Load a template from innerHTML of element specified by id
    addTemplate: function(name, id) {
      this.templates[name] = $(id).html()
    },

    // Expand a template with the given data
    expandTemplate: function(templateName, data) {
      var html = this.templates[templateName] || '';
      var expander = function(fullmatch, key) {
          k = key.toLowerCase()
          return k in data ? data[k] : fullmatch;
      }
      html = html.replace(/<!--#([^#]+)#-->/g, expander);
      return html.replace(/#([^#]+)#/g, expander);
    },

    getCookie: function (name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = jQuery.trim(cookies[i]);
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) == (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
    },
    csrfSafeMethod: function (method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    },
    sameOrigin: function (url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    },
    getOrderBy: function(old_order, new_order) {
      var desc = false,
          old_desc = false;
      if (old_order.match(/^\-/)) {
          old_order = old_order.replace(/^\-/, '')
          old_desc = true;
      }
      if (new_order == old_order)
          desc = !old_desc;
      return (desc ? '-' : '') + new_order;
    },
    setOrderByClasses: function(elem, list, orderkey) {
      $(list).removeClass('orderby').removeClass('orderby-desc')
      $(elem).addClass(orderkey.match(/^-/) ? 'orderby-desc' : 'orderby');
    },
    insertToOrderedList: function(topElem, selector, matcher, elem, defaultInsertCallback) {
      var inserted = false,
        lastInsert = defaultInsertCallback || function() {
          elem.detach().appendTo($(topElem));
        }

      $(topElem).children(selector).each(function() {
        var currentElem = $(this);
        if(matcher(currentElem)) {
          elem.detach().insertBefore(currentElem);
          inserted = true;
        }
        return !inserted;
      });

      if(!inserted)
        lastInsert(elem)
    },
    setupJobInfoButtons: function(rootElem) {
      var t = this;
      $(rootElem).find('.jobinfobutton').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        t.showJobInfo(this)
      })
    },
    showJobInfo: function(triggerElem) {
      var t = this;
      triggerElem = $(triggerElem);
      var id = triggerElem.attr('data-pk');
      var popover = $('#jobinfo-popover');
      if(id == this.shownJobInfo && popover.is(":visible")) {
        popover.hide();
        return false;
      }
      var title = triggerElem.attr('title') || 'Job-info';
      $('#jobinfo-title').html(title);
      $('#jobinfo-content').html("Loading...");
      this.positionJobInfo(triggerElem);
      popover.show()
      this.shownJobInfo = id;
      var url = location.href.match(/^(https?:\/\/[^\/]+\/site\/[^\/]+\/)/);
      if (url) {
        url = url[1] + 'jobs/' + id + '/info/';
      } else {
        return false;
      }
      $.ajax({
        'type': 'GET',
        'url': url,
        'success': function(data) {
          $('#jobinfo-content').html(data)
          t.positionJobInfo(triggerElem)
        },
        'error': function() {
          $('#jobinfo-popover').hide();
        }
      })
      return false
    },
    positionJobInfo: function(refElem) {
      var offset = refElem.offset();
      var popover = $('#jobinfo-popover');
      popover.css({top: 0, left: 0});
      // Move left according to popover width
      offset.left -= popover.outerWidth();
      // Then right according to placement of arrow
      offset.left += 42;
      // And finally move to middle of trigger-element
      offset.left += (refElem.outerWidth() / 2);
      offset.top += refElem.outerHeight() + 5;
      $('#jobinfo-popover').css( {
        'top': offset.top + "px",
        'left': offset.left + "px",
      });
    },
    onBodyClick: function(e) {
      $('#jobinfo-popover').hide();
      return true;
    }
  })
  window.BibOS = window.BibOS || new BibOS();
  var b = window.BibOS;
  b.init();
  $(function() { b.onDOMReady() })

  // Setup support for CSRFToken in ajax calls
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!b.csrfSafeMethod(settings.type) && b.sameOrigin(settings.url)) {
        // Send the token to same-origin, relative URLs only.
        // Send the token only if the method warrants CSRF protection
        // Using the CSRFToken value acquired earlier
        xhr.setRequestHeader("X-CSRFToken", b.getCookie('csrftoken'));
      }
    }
  });

})($)


/* Function to show a spinner while we wait for a new page or content to load */

function spin() {
    $('body').append('<div class="overlay"><div class="windows8"><div class="wBall" id="wBall_1"><div class="wInnerBall"></div></div><div class="wBall" id="wBall_2"><div class="wInnerBall"></div></div><div class="wBall" id="wBall_3"><div class="wInnerBall"></div></div><div class="wBall" id="wBall_4"><div class="wInnerBall"></div></div><div class="wBall" id="wBall_5"><div class="wInnerBall"></div></div></div></div>');
};
