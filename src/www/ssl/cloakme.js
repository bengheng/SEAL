<!--

function Session() {
	this.server = "https://cloak.eecs.umich.edu/";
	this.username = "bengheng";
	this.password = "bengheng";
	this.sessionkey = false;
	this.alias = "myalias";
	this.hint = "myhint";
	this.domain = "testdomain";
}

Session.prototype = {

	init: function() {
		var self = this;
		self.getSessionkeyFromServer(self);

		//======================================================
		// Should not have anything after this that depends on
		// server results due to asynchronous calls.
	},


	getSessionkeyFromServer: function(self) {

		// Compute password md5. That's what the server should use.
		var pwdmd5 = MD5( self.password );
		
		// Prepares challenge
		var m = Math.floor(Math.random()*(2^32))+'';
		var mcipher = Aes.Ctr.encrypt(m, pwdmd5, 256);
		var n = Math.floor(Math.random()*(2^32))+'';
		var xmlHttpReq = false;

		// Mozilla/Safari
		if (window.XMLHttpRequest) {
			self.xmlHttpReq = new XMLHttpRequest();
		}


		var getstr = self.server+'cgi-bin/session.py?u='+self.username+
			'&c='+mcipher+'&m='+m+'&n='+n;
		//document.write("GET: "+getstr+'\n');
					document.write("blablabla");
		self.xmlHttpReq.open('GET',	getstr, true);
		self.xmlHttpReq.setRequestHeader('Content-Type', 'text/html');
		self.xmlHttpReq.onreadystatechange = function() {
			if (self.xmlHttpReq.readyState == 4) {
				self.sessionkey = self.extractSessionKey(self,
					self.xmlHttpReq.responseText,
					pwdmd5,
					n);
				if (self.sessionkey == false ) {
					//dump( "No session key!\n" );
					document.write("blablabla");
					return;
				}
				self.xmlHttpReq.close;
				self.getAlias(self);
			}
			return;
		}
		self.xmlHttpReq.send();
	},

	getAliasRequest: function(self) {
		if (!self.sessionkey)
			return false;

		var data = {};
		data.user = self.username;
		data.domain = self.domain;
		if (self.hint != '')
			data.hint = self.hint;
		if (self.alias != '')
			data.alias = self.alias;

		var js = JSON.stringify(data);

		//dump("Using session key :\""+self.sessionkey+"\"\n");
		// Encrypt js with session key
		var cipher = Aes.Ctr.encrypt(js, self.sessionkey, 256);
		var req = {};
		req.user = self.username;
		req.c = cipher;
		return JSON.stringify(req);
	},

	extractSessionKey: function(self, str, password, n) {
		//document.write(str);	
		if (str == "INVALID USER\n") {
			//msg( "User not found!" );
			return false;
		}
		else if (str == "AUTH ERR\n") {
			//msg( "Invalid password!" );
			return false;
		}

		var plain = Aes.Ctr.decrypt(str, password, 256);
		// First four characters are length of JSON string
		var l = parseInt( plain.substr(0, 4), 16 );
		var js = plain.substr(4, l);
		var j = JSON.parse(js);
		if ( j.n != n) {
			//dump("n doesn't match!\n");
			// n doesn't match!
			return false;
		}

		//self.sessionkey = j.k;
		//dump("Server gave session key: "+self.sessionkey+"\n");
		return j.k;
	},

	getAlias: function(self) {
		var xmlHttpReq = false;
		var plaintext = self.domain;
		if (!plaintext) {
			return;
		}

		var req = self.getAliasRequest(self);

		// Mozilla/Safari
		if (window.XMLHttpRequest) {
			self.xmlHttpReq = new XMLHttpRequest();
		}

		areq = btoa(req);
		self.xmlHttpReq.open('GET', self.server+'cgi-bin/getalias.py?r='+areq, true)
		self.xmlHttpReq.setRequestHeader('Content-Type', 'text/html');
		self.xmlHttpReq.onreadystatechange = function() {
			if (self.xmlHttpReq.readyState == 4) {
				self.replaceFocusedEleVal(self.xmlHttpReq.responseText);
				self.xmlHttpReq.close;
			}
			return;
		}
		self.xmlHttpReq.send();
	},

	replaceFocusedEleVal: function(str) {
		if (str.search("ERR") == 0) {
			//msg( str );
			return;
		}

		document.write(str);
		//document.getElementById("email").innerHTML=str;
		//document.close();
		return;
	},

}


var sess = new Session();
//setTimeout(function(sess) {sess.init();}, 1000, sess);
//var t = setTimeout( "sess.init()", 1000 );
sess.init();
//document.close();

-->
