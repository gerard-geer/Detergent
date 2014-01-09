$(function()
{
	// Get the user's playlist contents
	// and put them in the textarea.
	$('#input_textarea').text($('#playlist_contents').text());
	
	// Get the user's name
	// and update the welcome message.
	$('#welcome').text(  $('#current_user').text() + ', welcome to...' );
});