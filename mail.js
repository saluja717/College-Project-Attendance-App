class MailSender{
    nodemailer;
    gmail;
    mailfrom;
    tomail;
    sub;
    message;
    
    constructor(to, sub, msg){
        this.mailfrom = 'attendance@ashsec.sly.io';
        this.tomail = to;
        this.sub = sub;
        this.message = msg;
        this.nodemailer = require('nodemailer');
        this.gmail = this.nodemailer.createTransport({
          host: 'smtp.eu.mailgun.org',
          port: 587,
          secure: false,
          auth: {
              user: "postmaster@ashsec.sly.io",
              pass: "4930a8e7e0b737494cc0e4838192d3af-fe066263-63131442" 
          }
      });
    };  
  
    send(){
      console.log("sending mail")
      var mailOptions = {
        from: this.mailfrom,
        to: this.tomail,
        subject: this.sub,
        html: this.message,
        //html: "<b>From Capture It</b>", // html body
      };
      
      this.gmail.sendMail(mailOptions, function(error, info){
        if (error) {
          console.log(error);
        } else {
          console.log('Email sent: ' + info.response);
        }
      });
  };

}

module.exports = MailSender;

