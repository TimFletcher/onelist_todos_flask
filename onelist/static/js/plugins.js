window.log = function(){
  log.history = log.history || [];
  log.history.push(arguments);
  arguments.callee = arguments.callee.caller;  
  if(this.console) console.log( Array.prototype.slice.call(arguments) );
};
(function(b){function c(){}for(var d="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),a;a=d.pop();)b[a]=b[a]||c})(window.console=window.console||{});

/*
 * jQuery autoResize (textarea auto-resizer)
 * @copyright James Padolsey http://james.padolsey.com
 * @version 1.04
 */
(function($){$.fn.autoResize=function(options){var settings=$.extend({onResize:function(){},animate:true,animateDuration:150,animateCallback:function(){},extraSpace:20,limit:1000},options);this.filter('textarea').each(function(){var textarea=$(this).css({resize:'none','overflow-y':'hidden'}),origHeight=textarea.height(),clone=(function(){var props=['height','width','lineHeight','textDecoration','letterSpacing'],propOb={};$.each(props,function(i,prop){propOb[prop]=textarea.css(prop)});return textarea.clone().removeAttr('id').removeAttr('name').css({position:'absolute',top:0,left:-9999}).css(propOb).attr('tabIndex','-1').insertBefore(textarea)})(),lastScrollTop=null,updateSize=function(){clone.height(0).val($(this).val()).scrollTop(10000);var scrollTop=Math.max(clone.scrollTop(),origHeight)+settings.extraSpace,toChange=$(this).add(clone);if(lastScrollTop===scrollTop){return}lastScrollTop=scrollTop;if(scrollTop>=settings.limit){$(this).css('overflow-y','');return}settings.onResize.call(this);settings.animate&&textarea.css('display')==='block'?toChange.stop().animate({height:scrollTop},settings.animateDuration,settings.animateCallback):toChange.height(scrollTop)};textarea.unbind('.dynSiz').bind('keyup.dynSiz',updateSize).bind('keydown.dynSiz',updateSize).bind('change.dynSiz',updateSize)});return this}})(jQuery);

// jQuery plugin: PutCursorAtEnd 1.0
// http://plugins.jquery.com/project/PutCursorAtEnd
// by teedyay
//
// Puts the cursor at the end of a textbox/ textarea

(function($)
{jQuery.fn.putCursorAtEnd=function()
{return this.each(function()
{$(this).focus()
if(this.setSelectionRange)
{var len=$(this).val().length*2;this.setSelectionRange(len,len);}
else
{$(this).val($(this).val());}
this.scrollTop=999999;});};})(jQuery);

/*
    A simple jQuery modal (http://github.com/kylefox/jquery-modal)
    Version 0.2.2
*/
(function(){var current_modal=null;$.fn.modal=function(options){var $elm=$(this);if($elm.attr('href')){$elm.click(open_modal_from_link);return;}
options=$.extend({},$.fn.modal.defaults,options);function block(){current_modal.blocker=$('<div class="jquery-modal blocker"></div>').css({top:0,right:0,bottom:0,left:0,width:"100%",height:"100%",position:"fixed",zIndex:options.zIndex,background:options.overlay,opacity:options.opacity});if(options.escapeClose){$(document).keydown(function(event){if(event.which==27){$.fn.modal.close();}});}
if(options.clickClose){current_modal.blocker.click($.fn.modal.close);}
$('body').append(current_modal.blocker);$elm.trigger($.fn.modal.BLOCK,[current_modal]);}
function show(){center_modal(current_modal);if(options.showClose){current_modal.closeButton=$('<a href="#close-modal" rel="modal:close" class="close-modal">Close</a>');current_modal.elm.append(current_modal.closeButton);}
$elm.addClass(options.modalClass).addClass('current').show();$elm.trigger($.fn.modal.OPEN,[current_modal]);}
current_modal={elm:$elm,options:options};$elm.trigger($.fn.modal.BEFORE_BLOCK,[current_modal]);block();$elm.trigger($.fn.modal.BEFORE_OPEN,[current_modal]);show();};$.fn.modal.defaults={overlay:"#000",opacity:0.75,zIndex:1,escapeClose:true,clickClose:true,modalClass:"modal",showClose:true};$.fn.modal.BEFORE_BLOCK='modal:before-block';$.fn.modal.BLOCK='modal:block';$.fn.modal.BEFORE_OPEN='modal:before-open';$.fn.modal.OPEN='modal:open';$.fn.modal.BEFORE_CLOSE='modal:before-close';$.fn.modal.CLOSE='modal:close';$.fn.modal.close=function(event){if(event){event.preventDefault();}
if(!current_modal){return;}
current_modal.elm.trigger($.fn.modal.BEFORE_CLOSE,[current_modal]);if(current_modal.closeButton){current_modal.closeButton.remove();}
current_modal.blocker.remove();current_modal.elm.hide();current_modal.elm.trigger($.fn.modal.CLOSE,[current_modal]);current_modal=null;};$.fn.modal.resize=function(){center_modal(current_modal);};function open_modal_from_link(event){event.preventDefault();var target=$(this).attr('href');if(target.match(/^#/)){$(target).modal();}else{$.get(target,{},function(html){$(html).appendTo('body').bind('modal:close',function(event,modal){modal.elm.remove();}).modal();});}}
function center_modal(modal){modal.elm.css({position:'fixed',top:"50%",left:"50%",marginTop:-(modal.elm.outerHeight()/2),marginLeft:-(modal.elm.outerWidth()/2),zIndex:modal.options.zIndex+1});};$('a[rel="modal:open"]').live('click',open_modal_from_link);$('a[rel="modal:close"]').live('click',$.fn.modal.close);})();