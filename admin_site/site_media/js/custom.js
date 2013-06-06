// Set up global BibOS instance used for accessing utility methods
var BibOS;
(function($) {
  function BibOS(args) {
    this.templates = {};
  }

  $.extend(BibOS.prototype, {
    init: function() {
    },

    onDOMReady: function() {
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
          return k in data ? (data[k] || '') : fullmatch;
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

