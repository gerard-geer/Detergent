
/*
	Initializes the page upon first load.
*/
function init()
{
	// Attach functionality to the URL box.
	$('#url_text_submit').submit(onAddressUpload);
	console.log($('#song_list'));
	initPlaylistPane();
}

/*
	Initializes the upload pane.
*/
function initUploadPane()
{
}

/*
	Initializes the playlist pane.
*/
function initPlaylistPane()
{
	loadSongs();
	$('#song_list').selectable();
	console.log("SDF");
}
