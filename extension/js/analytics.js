// Analytics configuration for DealFlow Analytics
// Replace 'YOUR_MIXPANEL_TOKEN' with your actual token from mixpanel.com

const Analytics = {
  // Get your token from: https://mixpanel.com/project/settings
  MIXPANEL_TOKEN: 'YOUR_MIXPANEL_TOKEN', // TODO: Replace with actual token
  
  // Initialize analytics
  init: function() {
    if (this.MIXPANEL_TOKEN === 'YOUR_MIXPANEL_TOKEN') {
      console.warn('Analytics: Please add your Mixpanel token');
      return;
    }
    
    // Load Mixpanel library
    (function(f,b){if(!b.__SV){var e,g,d,h;window.mixpanel=b;b._i=[];b.init=function(e,f,c){function g(a,d){var b=d.split(".");2==b.length&&(a=a[b[0]],d=b[1]);a[d]=function(){a.push([d].concat(Array.prototype.slice.call(arguments,0)))}}var a=b;"undefined"!==typeof c?a=b[c]=[]:c="mixpanel";a.people=a.people||[];a.toString=function(a){var d="mixpanel";"mixpanel"!==c&&(d+="."+c);a||(d+=" (stub)");return d};a.people.toString=function(){return a.toString(1)+".people (stub)"};d="disable time_event track track_pageview track_links track_forms track_with_groups add_group set_group remove_group register register_once alias unregister identify name_tag set_config reset opt_in_tracking opt_out_tracking has_opted_in_tracking has_opted_out_tracking clear_opt_in_out_tracking start_batch_senders people.set people.set_once people.unset people.increment people.append people.union people.track_charge people.clear_charges people.delete_user people.remove".split(" ");
    for(h=0;h<d.length;h++)g(a,d[h]);var i="set set_once union unset remove delete".split(" ");a.get_group=function(){function b(c){d[c]=function(){call2_args=arguments;call2=[c].concat(Array.prototype.slice.call(call2_args,0));a.push([e,call2])}}for(var d={},e=["get_group"].concat(Array.prototype.slice.call(arguments,0)),c=0;c<i.length;c++)b(i[c]);return d};b._i.push([e,f,c])};b.__SV=1.2;e=f.createElement("script");e.type="text/javascript";e.async=!0;e.src="undefined"!==typeof MIXPANEL_CUSTOM_LIB_URL?MIXPANEL_CUSTOM_LIB_URL:"file:"===f.location.protocol&&"//cdn.mxpnl.com/libs/mixpanel-2-latest.min.js".match(/^\/\//)?"https://cdn.mxpnl.com/libs/mixpanel-2-latest.min.js":"//cdn.mxpnl.com/libs/mixpanel-2-latest.min.js";g=f.getElementsByTagName("script")[0];g.parentNode.insertBefore(e,g)}})(document,window.mixpanel||[]);
    
    mixpanel.init(this.MIXPANEL_TOKEN);
  },
  
  // Track events
  track: function(event, properties = {}) {
    if (this.MIXPANEL_TOKEN === 'YOUR_MIXPANEL_TOKEN') {
      console.log(`Analytics (disabled): ${event}`, properties);
      return;
    }
    
    // Add common properties
    const enrichedProperties = {
      ...properties,
      extension_version: chrome.runtime.getManifest().version,
      timestamp: new Date().toISOString()
    };
    
    if (typeof mixpanel !== 'undefined') {
      mixpanel.track(event, enrichedProperties);
    }
  },
  
  // Identify user
  identify: function(userId) {
    if (typeof mixpanel !== 'undefined' && userId) {
      mixpanel.identify(userId);
    }
  },
  
  // Track user properties
  people: {
    set: function(properties) {
      if (typeof mixpanel !== 'undefined') {
        mixpanel.people.set(properties);
      }
    },
    increment: function(property, value = 1) {
      if (typeof mixpanel !== 'undefined') {
        mixpanel.people.increment(property, value);
      }
    }
  }
};

// Initialize on load
Analytics.init();

// Track extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    Analytics.track('Extension Installed');
  } else if (details.reason === 'update') {
    Analytics.track('Extension Updated', {
      previous_version: details.previousVersion
    });
  }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Analytics;
}