$(function()
{
	// The time it takes for the button to reset upon submission.
	var resetTime = 1000;
	
	// Get the user's playlist contents
	// and put them in the textarea.
	$('#input_textarea').text($('#playlist_contents').text());
	
	// Get the user's name
	// and update the welcome message.
	$('#welcome').text(  $('#current_user').text() + ', welcome to...' );
	
	var form = $('#input');
	var inputbutton = $('#input_submit');
	var textarea = $('#input_textarea');

	inputbutton.on('click', function(e) {
		console.log("sdtu");
		console.log(textarea.html());
		e.preventDefault();
		$.ajax( {
			type: 'POST',
			url: form.attr('action'),
			data: textarea.val(),
			success: function( response ) {
				setButtonNotifyState(inputbutton, true);
				int = setInterval(function(){
					setButtonNotifyState(inputbutton, false);
					clearInterval(int);
				}, resetTime);
			}
		} );
		}
	);
});

function setButtonNotifyState(button, state)
{
	if(state)
	{
		button.text('Playlist updated!');
		button.prop('disabled', true);
	}
	else
	{
		button.text('Update playlist');
		button.prop('disabled', false);
	}
	// Invert the styling colors of the button.
	button.css( {'color':button.css('background-color'), 'background-color':button.css('color')} );
}