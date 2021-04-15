# Jekyll Sharepoint

Ok... have you ever had that idea that seems completely nuts, but just also 
a little bit fun, and a litte bit useful? 

Well, this is one of those. Whilst working some FAQ / Knowledge Management
content for Social Finance, I found that maintaining and structuring content
in SharePoint takes a lot of preparation and thinking and changing things 
later is... not easy.

Yeah, yeah... lists and power apps and all that goodness is very powerful, but
sometimes you just want something simple that works. 

And Jekyll is awesome. So, here it is... a tool that can publish
your Jekyll site to sharepoint. 

The how-to manual is still a WiP because I have real work to do as well, 
but if you're interested, get in touch.

## Using personal credentials

Use MSAL - add examples.

## Using app credentials

Use Office365-REST-Python-Client

Register new app:

https://<tenant>.sharepoint.com/sites/<sitename>/_layouts/15/appregnew.aspx

Then grant permissions:

https://<tenant>.sharepoint.com/sites/<sitename>/_layouts/15/appinv.aspx

<AppPermissionRequests AllowAppOnlyPolicy="true">
  <AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web" Right="FullControl" />
</AppPermissionRequests>
