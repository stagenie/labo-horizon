import { Component, useProps } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { formatFloat } from "@web/core/utils/numbers";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class LabGaugeField extends Component {
    static template = "lab_owl.LabGaugeField";
    props = useProps({ ...standardFieldProps });

    get data() {
        return this.props.record.data;
    }

    /** Un point n'a de sens que pour une valeur chiffrée comparée à un vrai intervalle. */
    get hasValue() {
        return ["low", "normal", "high"].includes(this.data.flag) && this.data.range_max > this.data.range_min;
    }

    /** Position du point de 0 à 100 : l'intervalle de référence occupe le milieu (25 % → 75 %). */
    get percent() {
        const min = this.data.range_min;
        const span = this.data.range_max - min;
        const ratio = (this.data[this.props.name] - (min - span / 2)) / (span * 2);
        return Math.round(Math.min(Math.max(ratio, 0), 1) * 100);
    }

    get markerClass() {
        return this.data.flag === "normal" ? "bg-success" : "bg-danger";
    }

    get tooltip() {
        const f = (value) => formatFloat(value, { digits: [16, 2] });
        const unit = this.data.unit ? ` ${this.data.unit}` : "";
        return `${f(this.data[this.props.name])}${unit} (${f(this.data.range_min)} – ${f(this.data.range_max)})`;
    }
}

export const labGaugeField = {
    component: LabGaugeField,
    displayName: _t("Jauge de référence"),
    supportedTypes: ["float"],
    fieldDependencies: [
        { name: "range_min", type: "float" },
        { name: "range_max", type: "float" },
        { name: "unit", type: "char" },
        { name: "flag", type: "selection" },
    ],
};

registry.category("fields").add("lab_gauge", labGaugeField);
