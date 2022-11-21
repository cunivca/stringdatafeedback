/** @odoo-module **/
/* global checkVATNumber */

import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { useChildRef } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { CharField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";
import { loadJS } from "@web/core/assets";

import { usePartnerAutocomplete } from "@partner_ares/js/partner_ares_core"

export class PartnerAutoCompleteCharField extends CharField {
    setup() {
        super.setup();

        // Zde se ulozi data ziskane v souboru partner_ares_core
        this.partner_ares = usePartnerAutocomplete();

        // Reprezentuje input z kama se ctou uzivateluv vstup
        this.inputRef = useChildRef();
        useInputField({ getValue: () => this.props.value || "", parse: (v) => this.parse(v), ref: this.inputRef});
    }

    sanitizeVAT(request) {
        return request ? request.replace(/[^A-Za-z0-9]/g, '') : '';
    }

    isVAT(request) {
        // checkVATNumber is defined in library jsvat.
        // It validates that the input has a valid VAT number format
        return checkVATNumber(this.sanitizeVAT(request));
    }

    validateSearchTerm(request) {
        if (this.props.name == 'vat') {
            return this.isVAT(request);
        }
        else {
            return request && request.length > 2;
        }
    }

    get sources() {
        // Funkce, ktera vraci nalezene suggestions

        return [
            {
                options: async (request) => {

                    // Lazyload jsvat only if the component is being used.
                    await loadJS("/partner_ares/static/src/lib/jsvat.js");

                    // Pokud jsou v inputu aspon 3 znaky, nebo je ve vat cele platne cislo vat
                    if (this.validateSearchTerm(request)) {

                        const suggestions = await this.partner_ares.autocomplete(request, this.isVAT(request));

                        suggestions.forEach((suggestion) => {
                            suggestion.classList = "partner_ares_dropdown_char";
                        });

                        return suggestions;
                    }

                    // pokud neni validni vstup, tak nic nedelej a vrat prazdny list
                    else {
                        return [];
                    }
                },

                optionTemplate: "partner_ares.CharFieldDropdownOption",
                placeholder: _t('Searching Autocomplete...'),
            },
        ];
    }

    async onSelect(option) {
        // Funkce, ktera se provede po kliknuti na nekterou firmu

        const data = await this.partner_ares.getCreateData(Object.getPrototypeOf(option));

        // todo mozna smazat, jelikoz zadne logo v aresu neni
        if (data.logo) {
            const logoField = this.props.record.resModel === 'res.partner' ? 'image_1920' : 'logo';
            data.company[logoField] = data.logo;
        }

        // Some fields are unnecessary in res.company
        if (this.props.record.resModel === 'res.company') {
            const fields = ['comment', 'child_ids', 'additional_info'];
            fields.forEach((field) => {
                delete data.company[field];
            });
        }

        // Format the many2one fields
        const many2oneFields = ['country_id', 'state_id'];
        many2oneFields.forEach((field) => {
            if (data.company[field]) {
                data.company[field] = [data.company[field].id, data.company[field].display_name];
            }
        });
        this.props.record.update(data.company);
    }
}


// Bere se ze slozky ../xml/partner_ares.PartnerAutoCompleteCharField
PartnerAutoCompleteCharField.template = "partner_ares.PartnerAutoCompleteCharField";

// Prida do nove vytvoreneho pole componenty
PartnerAutoCompleteCharField.components = {
    ...CharField.components,
    AutoComplete,
};

// Registruje novy widget pro pole pod nazvem field_partner_ares
registry.category("fields").add("field_partner_ares", PartnerAutoCompleteCharField);
