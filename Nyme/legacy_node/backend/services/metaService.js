// backend/services/metaService.js
const axios = require('axios');

class MetaService {
    constructor() {
        this.baseUrl = `https://graph.facebook.com/${process.env.META_API_VERSION || 'v17.0'}/${process.env.META_PHONE_NUMBER_ID}`;
        this.token = process.env.META_ACCESS_TOKEN;
    }

    async sendText(to, text) {
        return this._request('messages', {
            messaging_product: "whatsapp",
            recipient_type: "individual",
            to: to,
            type: "text",
            text: { body: text }
        });
    }

    async sendTemplate(to, templateName, languageCode = 'es_MX', components = []) {
        return this._request('messages', {
            messaging_product: "whatsapp",
            recipient_type: "individual",
            to: to,
            type: "template",
            template: {
                name: templateName,
                language: { code: languageCode },
                components: components
            }
        });
    }

    async _request(endpoint, data) {
        try {
            const response = await axios.post(`${this.baseUrl}/${endpoint}`, data, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Meta API Error:', error.response?.data || error.message);
            throw error;
        }
    }
}

module.exports = new MetaService();
