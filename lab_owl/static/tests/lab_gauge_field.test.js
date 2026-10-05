import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { expect, test } from "@odoo/hoot";
import { queryOne } from "@odoo/hoot-dom";
import { defineModels, fields, models, mountView } from "@web/../tests/web_test_helpers";

class LabResult extends models.Model {
    _name = "lab.result";

    value = fields.Float();
    range_min = fields.Float();
    range_max = fields.Float();
    unit = fields.Char();
    flag = fields.Selection({
        selection: [["pending", "En attente"], ["low", "Bas"], ["normal", "Normal"], ["high", "Haut"], ["text", "Texte"]],
    });

    _records = [
        { id: 1, value: 0.9, range_min: 0.7, range_max: 1.1, unit: "g/L", flag: "normal" },
        { id: 2, value: 3.0, range_min: 0.7, range_max: 1.1, unit: "g/L", flag: "high" },
        { id: 3, value: 0, range_min: 0.7, range_max: 1.1, unit: "", flag: "text" },
        { id: 4, value: 5, range_min: 0, range_max: 0, unit: "", flag: "normal" },
    ];
}

defineMailModels();
defineModels([LabResult]);

/** La vue n'affiche que la valeur : les bornes et le drapeau arrivent par fieldDependencies. */
async function mountGauge(resId) {
    await mountView({
        type: "form",
        resModel: "lab.result",
        resId,
        arch: `<form><field name="value" widget="lab_gauge" readonly="1"/></form>`,
    });
}

test("normal value sits green in the middle", async () => {
    await mountGauge(1);
    expect(".o_lab_gauge_marker").toHaveClass("bg-success");
    expect(queryOne(".o_lab_gauge_marker").getAttribute("style")).toInclude("calc(50% - 5px)");
});

test("high value is red and clamped to the right edge", async () => {
    await mountGauge(2);
    expect(".o_lab_gauge_marker").toHaveClass("bg-danger");
    expect(queryOne(".o_lab_gauge_marker").getAttribute("style")).toInclude("calc(100% - 5px)");
});

test("dash for text result", async () => {
    await mountGauge(3);
    expect(".o_lab_gauge").toHaveCount(0);
    expect(".o_field_widget").toHaveText("—");
});

test("dash without reference range", async () => {
    await mountGauge(4);
    expect(".o_lab_gauge").toHaveCount(0);
});

test("loads neighbour fields itself", async () => {
    await mountGauge(1);
    expect(".o_lab_gauge").toHaveAttribute("data-tooltip", "0.90 g/L (0.70 – 1.10)");
});
