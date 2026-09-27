/*
  One place for the studio's contact details, so a number only ever has to be
  changed once. `display` is what people read; the other field is what the
  link uses.
*/
export const WHATSAPP_NUMBER = '918287633479';
export const WHATSAPP_DISPLAY = '+91 82876 33479';

export const PHONE_NUMBER = '+919876543210';
export const PHONE_DISPLAY = '+91 98765 43210';

export const EMAIL = 'hello@betterhomes.in';

export const STUDIO_ADDRESS =
  '170 2nd Block, Banashankari 6th Stage 1st Block, Channasandra, Bengaluru, Karnataka 560098';
export const STUDIO_HOURS = 'Mon–Sat, 10AM–7PM';

/* Opens WhatsApp with the message already drafted. */
export const whatsappLink = (message) =>
  `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;

export const ESTIMATE_MESSAGE = [
  'Hello Better Homes!',
  '',
  "I'd like a *free estimate* for my home.",
  '',
  'My name:',
  'Where the home is:',
  'What I need (full home / kitchen / bedroom / living):',
  'Rough size (e.g. 2BHK, 1200 sq ft):',
  'When I would like to start:',
  '',
  'Please get back to me with the scope and estimate. Thank you!'
].join('\n');

export const ESTIMATE_LINK = whatsappLink(ESTIMATE_MESSAGE);
