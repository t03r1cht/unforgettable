function success_notification() {
    $(".success").click(function () {
        window.onload = function () {
            $.bootstrapGrowl('We do have the Kapua suite available.', {
                type: 'success',
                delay: 2000,
            });
        };
        console.log("window.onload test");
    };
}