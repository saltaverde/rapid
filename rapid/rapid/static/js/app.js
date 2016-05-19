
/* ----------------------------------------------------------- */
/*  1. HEADER CONTENT SLIDE (SLICK SLIDER)
/* ----------------------------------------------------------- */

$(document).ready(function() {
  $('#forgot-password-link').click(function(e) {
    e.preventDefault();
    $('div#form-forgot-password-wrapper').toggle('500');
  });
  $('#forgot-password-link').click(function(e) {
    e.preventDefault();
    $('div#form-login-wrapper').toggle('500');
    $('#box_text span').text('RAPID Frogot Password?');
  });
  $('#access').click(function(e) {
    e.preventDefault();
    $('div#form-login-wrapper').toggle('500');
    $('#box_text span').text('RAPID Login');
  });
  $('#access').click(function(e) {
    e.preventDefault();
    $('div#form-forgot-password-wrapper').toggle('500');
  });
});
