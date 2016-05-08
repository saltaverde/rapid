
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
  });
  $('#access1').click(function(e) {
    e.preventDefault();
    $('div#form-login-wrapper').toggle('500');
  });
  $('#access1').click(function(e) {
    e.preventDefault();
    $('div#form-forgot-password-wrapper').toggle('500');
  });
});

$(document).ready(function() {
  $('#register-link').click(function(e) {
    e.preventDefault();
    $('div#form-register-wrapper').toggle('500');
  });
  $('#register-link').click(function(e) {
    e.preventDefault();
    $('div#form-login-wrapper').toggle('500');
  });
  $('#access2').click(function(e) {
    e.preventDefault();
    $('div#form-login-wrapper').toggle('500');
  });
  $('#access2').click(function(e) {
    e.preventDefault();
    $('div#form-register-wrapper').toggle('500');
  });
});