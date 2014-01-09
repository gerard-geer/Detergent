/*
	The CSH SOAP Web server.
	
	This Node.js server serves a portal for users to update and view
	SOAP playlists.
*/

// Module dependencies.
var http = require('http');
var fs = require('fs');
var qs = require('querystring');
var crypto = require('crypto');
var redis = require('redis');
var Cookies = require('cookies');
//var krb5 = require('node-krb5');

// Print a glorious banner.
process.stdout.write( 
"\n**************************************************************\n"+
"*                        CSH SOAP Server                     *\n"+
"* Letting you scrub-a-dub-dub with a wub-wub-wub since 2014. *\n"+
"* ---------------------------------------------------------- *\n"+
"**************************************************************\n");

var redis_host = '127.0.0.1';
var redis_port = 6379;
var redis_pw = 'shitty_password';

var playlistDelim = '-playlist';

var authRealm = 'csh.rit.edu';

var cryptoPW = 'aFF3Ef6q';
var cryptoType = 'aes-256-cbc';

/*
	Loads static files from the given path, and pipe-writes them 
	to the response based on the given MIME type.
	
	Parameters:
		res (Node.JS response):	The HTML response given by the server.
		
		path (String): 	The file-path to the file to serve.
		
		type (String):	The MIME type of the file being served.
*/
function serveStatic(res, path, type)
{
	// Write the header,
	res.writeHead(200, { 'Content-Type': type } );
	// and pipe the file into the response.
	fs.createReadStream(path).pipe(res);
}

/*
	Instead of loading a page, this simply writes out a very long
	String to the response, with the given MIME type.
	
	Parameters:
		res (Node.JS response):	The HTML response given by the server.
		
		page (String):	The content to be delivered.
		
		type (String):	The MIME type of that content.
*/
function serveDynamic(res, page, type)
{
	// Write the page header.
	res.writeHead(200, { 'Content-Type': type } );
	// Write the rest of the page at the end of the request.
	res.end(page);
}

/*
	Takes the raw input of the text area, and parses it into a list 
	of separate entries.
	
	Prerequisites:
		Newlines in the text area are formatted as "\r\n".
	
	Parameters:
		rawData (String): The raw data received from the text area.
	
	Returns:
		Each line of the text area's contents formatted as a list.
	
*/
function parseNewPlaylist(res, rawData, cookies)
{
	// Get the username from the cookie.
	var user = fetchAndDecrypt('username', cookies);
	
	// If the user cookie is bad, we serve the error page and
	// return. Otherwise we parse the playlist.
	if(user == null || user == '')
	{
		console.log("ERROR: bad user when updating playlist.");
		serveStatic(res, __dirname+'/webs/error.html', 'text\html');
		return;
	}
	
	// Parse the raw post request into a JSON object.
	var data = qs.parse(rawData);
	
	// Strip down to only the input from the text area.
	data = data.input_textarea;
	
	// Split the data into separate URLs.
	data = data.split("\r\n");
	
	// Get rid of any bad elements.
	var playlist = new Array();
	for(var i = 0; i < data.length; i++)
	{
		if(data[i] != '') playlist.push(data[i]);
	}
	
	// Log the newly parsed playlist to make sure things lined up.
	console.log("fresh playlist (user: "+user+"): ");
	console.log(playlist);
	
	
	// Send the playlist to redis.
	process.stdout.write("Storing "+user+"'s playlist... ");
	redisClient.del(user+playlistDelim, function(){
		redisClient.lpush(user+playlistDelim, playlist, function(){
			process.stdout.write("...done.\n");
		});
	});
	
		
	
	serveStatic(res, __dirname+'/webs/updated.html', 'text\html');	
}

/*
	Takes the raw authentication input from the appropriate POST
	request, parses it down, and tries to authenticate the user.
	
	Parameters:
	-res (HTTP Response):	The Node HTTP response stream used by
							by the current request.
	
	-rawData(String):	The credentials received through the 
						log-in form.
					
	-cookies(Cookies):	The Cookies instance used to store and read
		client-side cookies.
*/
function authenticate(res, rawData, cookies)
{
	var data = qs.parse(rawData);
	
	var user = data.input_user;
	
	//krb5.authenticate(user+'@'+authRealm, data.input_pw, function(err){
	var err = false;
		if(err)
		{
			console.log("invalid credentials tried.");
			serveStatic(res, __dirname+'/webs/invalid.html', 'text/html');
		}
		else
		{
			console.log(user+" has logged in.");
			encryptAndStore(user, 'username', cookies);
			prepareMainPage(res, user);
		}
	//});
	
	
}

/*
	Encrypts a value, and stores it as a cookie at the given key, with the given
	Cookies instance.
	
	Parameters:
		-value (String): 	The value to encrypt.
		
		-key (String):	The name of the cookie.
		
		-cookies (Cookies):	The Cookies instance to use for cookie storage.
*/
function encryptAndStore(value, key, cookies)
{
	var cipher = crypto.createCipher(cryptoType, cryptoPW);
	var encrypted = cipher.update(value, 'utf8', 'hex');
	encrypted += cipher.final('hex');
	cookies.set(key, encrypted);
}

/*
	Decrypts a cookie stored at the given key, retrieved by the given Cookies
	instance.
	
	Parameters:
		-key (String):	The name of the cookie.
		
		-cookies (Cookies):	The Cookies instance to use for cookie storage.
	
	Returns:
		-The decrypted value of the cookie.
*/
function fetchAndDecrypt(key, cookies)
{
	try{
		var encrypted = cookies.get(key);
		var decipher = crypto.createDecipher(cryptoType, cryptoPW);
		var decrypted = decipher.update(encrypted, 'hex', 'utf8');
		decrypted += decipher.final('utf8');
		return decrypted;
	}
	catch(e)
	{
		return null;
	}
}

/*
	Returns a sample playlist. Soon, when we can access the user
	and have the redis database set up it will query the database
	and get that user's pre-existing playlist.
	
	Parameters:
		user (String):	The user that whose playlist is needed.
		doneCallback(Array playlist):	A function to call when the Redis
			client has retrieved the user's playlist. It accepts a single
			argument that is an Array to pass in the retrieved playlist.
		
	Returns:
		A list of Strings that constitutes the user's playlist.
*/
function fetchExistingPlaylist(user, doneCallback)
{
	var playlist = new Array();
	
	// Get the playlist from Redis.
	process.stdout.write("Fetching "+user+"'s playlist... ");
	redisClient.lrange(user+playlistDelim, 0, -1, function(err, reply){
		var stringReply = String(reply);
		var elements = stringReply.split(',');
		process.stdout.write("...done.\n");
		doneCallback(elements);
	});
	return playlist;
}
	
/*
	Appends the current playlist as an invisible paragraph at the
	end of the page. Janky as fuck? Yes. More stable than server-side
	JQuery? Also yes.
	
	Parameters:
		page (String):	The raw HTML String that represents the webpage
						that we are appending the playlist to.
						
		playlist(String[]):	The list of strings that make up the user's
						existing playlist.
						
	Returns:
		The freshly modified page HTML, as a now slightly longer String.
		
*/
function appendPlaylist(page, playlist)
{
	// Append the opening paragraph tag.
	page+="<p id='playlist_contents' style='display:none;'>";
	
	// If the playlist is empty, we immediately close the appendage.
	if(playlist.length == 0)
	{
		page+="</p>";
		return page;
	}
	
	// Go through and format-poop the playlist into the paragraph.
	for(var i = 0; i < playlist.length-1; i++)
	{
		page+=playlist[i]+"\r\n";
	}
	// We append the final playlist item separately so we don't put
	// an extra line break.
	page+=playlist[playlist.length-1];
	
	// Add that closing tag.
	page+="</p>";
	
	// Return the page.
	return page;
}

/*
	Appends the current user's user name as an invisible paragraph at the
	end of the page.
	
	Parameters:
		page (String):	The raw HTML String that represents the webpage
						that we are appending the playlist to.
						
		username:	The list of strings that make up the user's
					existing playlist.
						
	Returns:
		The freshly modified page HTML, as a now slightly longer String.
		
*/
function appendUsername(page, username)
{
	// Append the thing.
	page+="<p id='current_user' style='display:none;'>"+username+"</p>";
	
	// Return the modified page.
	return page;
}

/*
	Performs all the operations that are required to display the main page,
	such as getting the user's existing playlist and adding it to the page
	so that it can be the default data in the main page's text area,
	and then serves it to the response.
	
	Parameters:
		res (Node HTML response):	The response given to us by the server.
		
		user (String):	The user's CSH user name.
*/
function prepareMainPage(res, user)
{
	// Create an empty String to store the page.
	var page = '';
	
	// Open up a file reading stream to load the file.
	var pageStream = fs.createReadStream(__dirname + '/webs/index.html');
	
	// Create file-loading callbacks.
	pageStream.on('data', function(chunk){ page+=chunk; } );
	pageStream.on('end', function(chunk){
		// Get the existing playlist.
		fetchExistingPlaylist(user, function(playlist){
			
			// Append the username to the page.
			page = appendUsername(page, user);
			
			// Append that playlist to the page.
			page = appendPlaylist(page, playlist);
			
			// Serve the freshly modified HTML to the client.
			serveDynamic(res, page, 'text/html');
		});
		
	});
}

/*
	The GET request router.
	Filters down input to requests for the main page, styling sheets, styling
	images, and JavaScript.
	
	Parameters:
		req (Node HTML request):	The HTML request stream.
		
		res (Node HTML response):	The HTML response stream.
*/
function onGetRequest(req, res, cookies)
{
	// If we go to the base page, we want to present the user with a log-in dialog
	// if they are not logged in. This requires us to check for our username cookie.
	if(req.url == '/')
	{
		var user = fetchAndDecrypt('username', cookies);
		
		if(user == '' || user == null)
		{
			serveStatic(res, __dirname +'/webs/auth.html', 'text/html');
		}
		else
		{
			console.log(user+" has returned with their cookie intact.");
			prepareMainPage(res, user);
		}
	}
	// CSS documents.
	else if(req.url.substr(0, 4) == '/css' && req.url.substr(-4) == '.css')
	{
		serveStatic(res, __dirname + '/webs'+req.url, 'text/css');
	}
	// Images.
	else if(req.url.substr(0, 4) == '/css' && req.url.substr(-4) == '.png')
	{
		serveStatic(res, __dirname + '/webs'+req.url, 'image/png');
	}
	// JavaScript.
	else if(req.url.substr(0, 3) == '/js' && req.url.substr(-3) == '.js')
	{
		serveStatic(res, __dirname + '/webs'+req.url, 'text/javascript');
	}
	// Sketchy GET requests get ditched.
	else
	{
		res.writeHead(404);
		res.end('Not found');
	}
}

/*
	The POST request router. This function has the job of snatching 
	user's playlists and doing stuff to them, as well as requesting
	credentials from the user.
	
	Parameters:
		req (Node HTML request):	The HTML request stream.
		
		res (Node HTML response):	The HTML response stream.
*/
function onPostRequest(req, res, cookies)
{
	// Make sure that the post request has the right URL.
	if(req.url == '/update')
	{
		// The data sent in the POST request.
		var data = '';
		
		// Accumulate the playlist form data.
		req.on('data', function(chunk){
							data+=chunk;
						});
		// When the last chunk is received we serve back the main 
		// website and parse the playlist data.
		req.on('end', function(){
							parseNewPlaylist(res, data, cookies);
						});
	}
	// Test the credentials given by the user.
	else if(req.url == '/auth')
	{
		// The data sent in the Post request.
		var data = '';
		
		// Accumulate the auth form data.
		req.on('data', function(chunk){
							data+=chunk;
						});
		// When the last chunk is received we authenticate the user.
		req.on('end', function(){
							authenticate(res, data, cookies);
						});
	}
	// Clear out the user's cookie upon logout.
	else if(req.url == '/logout')
	{
		var user = fetchAndDecrypt('username', cookies);
		
		if(user == '' || user == null)
			console.log("A user has logged out, but they corrupted their cookie somehow during use.");
		else
			console.log(user+" has logged out.");
			
		cookies.set('username', null);
		serveStatic(res, __dirname +'/webs/auth.html', 'text/html');
	}
		
	// Sketchy post requests get ditched.
	else
	{
		res.writeHead(404);
		res.end('...dude.');
	}
}


// Set up the Redis Client.
var redisClient = redis.createClient(redis_port, redis_host);
redisClient.auth(redis_pw);

redisClient.on('error', function (err){
	console.log('Redis Error: '+err);
});

redisClient.on('ready', function (){
	console.log('Redis ready!');
});


// Create the HTTP server, and set up request routing into the routing functions.
var server = http.createServer(function(req, res) {

	// Create a Cookies instance.
	cookies = new Cookies(req, res);
	
	// Send GET requests to the GET router.
	if(req.method == 'GET')
	{
		onGetRequest(req, res, cookies);
	}
	// Send POST requests to the POST router.
	else if(req.method == 'POST')
	{
		onPostRequest(req, res, cookies);
	}
	// Anything else gets tossed by the wayside.
	else
	{
		res.writeHead(404);
		res.end('Not found');
	}
});
// Set shit in motion.
server.listen(80);
