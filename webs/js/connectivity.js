
/*
	Inserts an indeterminant value JQuery UI loading bar 
	into the given parent element.
*/
function insertLoadingBar(parent)
{
	// Append our new element into the parent.
	$(parent).append('<div id="loading">Fetching song list from database...<div id="bar"></div></div>');
	// Make that element into a progress bar.
	$('#bar').progressbar( {value: false} );
	// Set up some CSS on that progress bar.
	$('#bar ui-progressbar-value').css({'background-color': '#cccccc'});
}

/*
	Deletes the loading bar from the given parent element 
	if the loading bar exists.
*/
function removeLoadingBar(parent)
{
	$(parent).children('#loading').remove();
}

/*
	Loads the songs from the database, handling the 
	progress bar as well.
*/
function loadSongs()
{
	// Start loading animation.
	insertLoadingBar('#playlist_box');
	// Load songs
	//  - Attach callback to replace loading animation when done
}

/*
	Creates and returns a DOM element String based on the given song.
*/
function createSong(song)
{
	return 	"<li class='playlist_element'>"+
					"<p class='song_content' id='filename'><p class='song_label'>Name:</p>"+song.n+"</p>"+
					"<p class='song_content' id='creator'><p class='song_label'>Creator:</p>"+song.c+"</p>"+
					"<p class='song_content' id='url'><p class='song_label'>url:</p>"+song.u+"</p>"+
			"</li>";
}

/*
	Connects to the server, queries the Redis database for
	the song list, constructs an Array of JQuery elements to
	represent the song, and returns the Array.
*/
function getSongsFromServer()
{
	// connect to server
	// query the shit out of the Redis database.
	// construct song objects 
	// return song objects
}

function displaySongs()
{
	// Draw the songs to the page and set them up to be
	// selectable.
}

function onPlaylistUpdate()
{
	// Hide button.
	// Start busy animation.
	// Get selected songs.
	// connect to Redis.
	// update Redis.
	// stop busy animation.
	// display confirmation.
	//  - attach callback to bring back the button after a bit.
}

function onSongUpload()
{
	// Hide button.
	// Start busy animation.
	// Connect to server.
	// Transfer song.
	//  - Server updates Redis.
	// stop busy animation.
	// display confirmation.
	//  - attach callback to bring back the button after a bit.
}

function onAddressUpload()
{
	valueEntered = document.forms["url_text_form"]["url_text_input"].value;
	alert("You entered: "+valueEntered);
	e.preventDefault();
	// Hide button.
	// Start busy animation.
	// Connect to server.
	// Transfer url text.
	//  - Server updates Redis.
	// stop busy animation.
	// display confirmation.
	// display confirmation.
	//  - attach callback to bring back the button after a bit.
}