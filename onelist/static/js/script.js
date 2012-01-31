UTIL = {
  fire : function(func,funcname, args){
    var namespace = ONELIST;
    funcname = (funcname === undefined) ? 'init' : funcname;
    if (func !== '' && namespace[func] && typeof namespace[func][funcname] == 'function'){
      namespace[func][funcname](args);
    }
  },
  loadEvents : function(){
    var bodyId = document.body.id;
    UTIL.fire('common');
    $.each(document.body.className.split(/\s+/),function(i,classnm){
      UTIL.fire(classnm);
      UTIL.fire(classnm,bodyId);
    });
    UTIL.fire('common','finalize');
  }
};

// kick it all off here 
$(document).ready(UTIL.loadEvents);
  
ONELIST = {
  common : {
    init : function(){

      // Prevent links from opening in Safari when running in app mode on iPhone
      $('a').live('click', function (event) {
        event.preventDefault();
        window.location = $(this).attr("href");
      });

      // Hash for keyboard
      key = {up: 38, down: 40, enter: 13, del: 8};

      // Flash Messages
      $('#flash-messages').delay(2500).fadeOut(300);

      // Show/Hide navigation
      $('#toggle-nav').click(function(){
          if ($('#header-nav a').is(':visible')) {
            $('#header-nav a').hide();
          } else {
            $('#header-nav a').css('display', 'block');
          };
      });

      // Hide navigation on a click away
      $(document).bind('click', function(e) {
        var clicked = $(e.target);
        if (! clicked.parents().hasClass('header-nav')) {
          $("#header-nav a").hide();
        }
      });

      // Form styling with inset labels
      function toggleLabel() {
        var input = $(this);
        setTimeout(function() {
          var def = input.attr('title');
          if (!input.val() || (input.val() == def)) {
            input.prev('span').css('visibility', '');
            if (def) {
              var dummy = $('<label></label>').text(def).css('visibility','hidden').appendTo('body');
              input.prev('span').css('margin-left', dummy.width() + 3 + 'px');
              dummy.remove();
            }
          } else {
            input.prev('span').css('visibility', 'hidden');
          }
        }, 0);
      };
      $('.onelist-form input, textarea').live('keydown', toggleLabel);
      $('.onelist-form input, textarea').live('paste', toggleLabel);
      $('.onelist-form select').live('change', toggleLabel);
      $('.onelist-form input, textarea').live('focusin', function() {
          $(this).prev('span').css('color', '#ccc');
      });
      $('.onelist-form input, .onelist-form textarea').live('focusout', function() {
          $(this).prev('span').css('color', '#999');
      });
      $('.onelist-form input, .onelist-form textarea').each(function() { toggleLabel.call(this); });
    },
    finalize : function(){}
  },
  accounts : {
    init : function(){
      // Focus first input on all forms
      $('input:first').focus();
    },
    login : function(){},
    register : function(){}
  },
  lists : {
    init : function(){

      disableTextarea = function() {
        $('#textarea-wrapper div').addClass('waiting').find('textarea').attr('readonly', 'readonly');
      };

      enableTextarea = function() {
        $('#textarea-wrapper div').removeClass('waiting').find('textarea').removeAttr('readonly');
      };

      $.ajaxSetup({
        error: function(jqXHR, textStatus, errorThrown){
          content  = '<ul id="flash-messages">\n';
          content += '  <li class="message-error">';
          if (textStatus == 'timeout') {
            content += 'The connection timed out. Is your Internet connection ok?';
          } else {
            content += 'The server returned an error. We\'re looking into it.';
          }
          content += '</li>\n';
          content += '</ul>';
          $(content).appendTo('header').delay(2500).fadeOut(300);
          enableTextarea();
        }
      });

      addItemCallback = function(data, textStatus, jqXHR){
        if (textStatus == 'success') {
          content  = '<li id="item-' + data.insert_id + '">';
          content += '  <a href="#" class="action-button delete rounded-3" data-id="'+data.insert_id+'" data-url="/list/delete/'+data.insert_id+'/">Delete</a>';
          content += '  <input type="checkbox" class="checkoff" data-id="'+data.insert_id+'" data-url="/list/checkoff/'+data.insert_id+'/">';
          content += '  <textarea id="item-'+data.insert_id+'-text" name="text-'+data.insert_id+'" data-id="'+data.insert_id+'" data-url="/list/edit/'+data.insert_id+'/">'+data.text+'</textarea>';
          content += '</li>';
          $(content).appendTo('#todo-item-list')
                    .find('textarea')
                    .autoResize({
                      animate: false,
                      extraSpace : 0
                    }).trigger('change');

          // Show flash message if we're adding by hash
          if (data.by_hash) {
            msg =  "<ul id='flash-messages'>";
            msg += "  <li class='message-info'>Item added successfully</li>";
            msg += "</ul>";
            $(msg).appendTo('header').delay(2500).fadeOut(300);
          }
          enableTextarea();
        }
      };

      addItem = function(form, textarea) {
        if (textarea.val().trim() == "") {
          textarea.focus();
        } else {
          disableTextarea();
          // Handle case where we're submitting by hash
          hash = form.find('#hash');
          if (hash.length) {
            url = '/list/add/' + hash.val() + '/'; // Can this be a generated URL?
          } else {
            url = form.attr('action');
          }
          $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            success: addItemCallback,
            dataType: 'json'
          });
          form.find('textarea').val('');
        }
      };

      // Add a new list item if the submit button is clicked or if the enter key
      // is pressed from within the input textarea.
      addNewItem = function(){
        form = $('#todo-add-form');
        textarea = form.find('#todo-add-textarea');
        textarea.focus();
        form.submit(function(){
            addItem(form, textarea);
            return false;
        });
        textarea.keydown(function(e) {
          var keyCode = e.keyCode ? e.keyCode : e.which;
          if (keyCode == key.enter) {
            addItem(form, textarea);
            return false;
          }
        });
      };

      updateItem = function(item) {
        $.ajax({
          type: 'POST',
          url: $(item).data().url,
          data: $(item).serialize(),
          success: function(data, textStatus, jqXHR){
            // If an attempt is made at saving a blank item it's deleted server
            // side. The response will contain the id_to_remove attribute which
            // we can test and remove the element if it exists.
            if (data.id_to_remove) {
              deleteItem($('#' + data.id_to_remove));
            }
          },
          dataType: 'json'
        });
      };

      deleteItem = function(item) {
        // Work out which item we should be giving focus to after the delete
        elem = item.next().find('textarea:eq(1)');
        if (elem.length) {
          elem.each(function(){
            subject = $(this);
          });
        } else {
          elem = item.prev().find('textarea:eq(1)');
          if (elem.length) {
            elem.each(function(){
              subject = $(this);
            });
          } else {
            // Focus the input textarea and hide the mode buttons.
            subject = $('#todo-add-form textarea');
          }
        }

        // Move focus as approprate
        subject.focus().putCursorAtEnd();

        // Remove item from the DOM first so we don't have to wait
        item.remove();

        // Delete item from the database in the background.
        $.ajax({
          type: 'POST',
          url: item.find('a.delete').data().url,
          data: {},
          success: deleteCallback,
          dataType: 'json'
        });
      };

      toggleCheckOffItem = function(item) {

        // Add checked off class
        item.toggleClass('checked-off');

        // Toggle checked off status for the item in the background.
        $.ajax({
          type: 'POST',
          url: item.find('.checkoff').data().url,
          data: {},
          success: checkOffItemCallback,
          dataType: 'json'
        });

        // Show delete button if item is checked off
        if (item.hasClass('checked-off')) {
          item.find('.delete').show();
        } else {
          item.find('.delete').hide();
        };
      };

      deleteCallback = function(data, textStatus, jqXHR){
      };

      checkOffItemCallback = function(data, textStatus, jqXHR){
      };
    },
    list : function(){
      // Ajax POST the new note on hitting enter within the add form's textfield.
      // On success we insert the returned text into the DOM as a new list item.
      addNewItem();
      $('#todo-add-textarea').focus().keydown(function(e){
        var keyCode = e.keyCode ? e.keyCode : e.which;
        if (keyCode == key.up) {
          elem = $(this).parents('#todo-list-container').find('#todo-item-list li:last-child textarea');
          if (elem.length) {
            elem.each(function(){
              $(this).focus().putCursorAtEnd();
            });
          }
          return false;
        }
      });

      // Automatically expand textareas
      $('#todo-item-list textarea').autoResize({
          animate: false,
          extraSpace : 0
      }).trigger('change');
      $('#todo-add-form textarea').autoResize({
          animateDuration : 100,
          extraSpace : 0
      });

      // Highlight item on focus
      $('#todo-item-list textarea').live('focus', function(){
        $(this).parent().addClass('focus');
      }).live('blur', function(){
        $(this).parent().removeClass('focus');
      });

      // Save item when:
      //  - It loses focus
      //  - The user hits enter
      //  - The user hits the up/down cursor key

      $('#todo-item-list textarea').blur(function(){
        updateItem(this);
      }).live('keydown', function(e){
          var keyCode = e.keyCode ? e.keyCode : e.which;
          key = {up: 38, down: 40, enter: 13, del: 8};
          switch (keyCode) {
            case key.up:
              elem = $(this).parent().prev().find('textarea:eq(1)');
              if (elem.length) {
                $(this).blur(); // Might be nowhere to go
                elem.each(function(){
                  $(this).focus().putCursorAtEnd();
                });
              }
              return false;
            break;
            case key.down:
              elem = $(this).parent().next().find('textarea:eq(1)');
              $(this).blur();
              if (elem.length) {
                elem.each(function(){
                  $(this).focus().putCursorAtEnd();
                });
              }
              return false;
            break;
            case key.enter:
              updateItem(this);
              elem = $(this).parent().next().find('textarea:eq(1)');
              $(this).blur();
              if (elem.length) {
                elem.each(function(){
                  $(this).focus().putCursorAtEnd();
                });
              } else {
                // Must be deleting the final item so focus input textarea.
                $('#todo-add-form textarea').focus().putCursorAtEnd();
              }
              return false;
            break;
            case key.del:
              if (e.metaKey) {
                deleteItem($(this).parent());
                return false;
              }
            break;
          }
          return true;
      });

      // Move to input textarea when hitting down arrow on final list textarea
      $('#todo-item-list li:last-child textarea').live('keydown', function(e){
        var keyCode = e.keyCode ? e.keyCode : e.which;
        switch (keyCode) {
          case key.down:
            $('#todo-add-textarea').focus().putCursorAtEnd();
            return false;
          break;
        }
        return true;
      });

      // Bind actions to delete buttons
      $('.delete').live('click', function(e){
        deleteItem($(this).parent());
        e.preventDefault();
        // return false;
        
      });

      // Bind actions to checkoff buttons
      $('.checkoff').live('click', function(e){
        toggleCheckOffItem($(this).parent());
      });

      // Modal for keyboard shortcuts
      $('#show-modal-keyboard-shortcuts').click(function(e){
        $('#modal-keyboard-shortcuts').modal({'showClose': false});
        return false;
      });
    },
    add : function(){
      addNewItem();
    }
  }
};